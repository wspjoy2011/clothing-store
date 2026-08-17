import datetime as datetime_lib
import secrets
from datetime import datetime, timedelta

from apps.accounts.dto.password_reset import PasswordChangeDTO, PasswordResetConfirmDTO, PasswordResetRequestDTO
from apps.accounts.dto.tokens import CreateTokenDTO
from apps.accounts.interfaces.repositories import (
    TokenRepositoryInterface,
    UserRepositoryInterface,
)
from apps.accounts.interfaces.services import PasswordServiceInterface
from apps.accounts.repositories.exceptions import TokenCreationError, TokenRepositoryError, UserUpdateError
from apps.accounts.services.exceptions import (
    ExpiredPasswordResetTokenError,
    IncorrectCurrentPasswordError,
    InvalidPasswordResetTokenError,
    PasswordChangeError,
    PasswordResetEmailError,
    PasswordResetError,
    PasswordResetRollbackError,
    PasswordResetTokenNotFoundError,
    SamePasswordError,
    UserNotFoundError,
    UserPasswordError,
)
from db.interfaces import TransactionManagerInterface
from notifications.email.interfaces import EmailSenderInterface
from notifications.exceptions.email import BaseEmailError
from security.exceptions import (
    EmptyPasswordError,
    HashingError,
    PasswordTooLongError,
    VerificationError,
)
from security.interfaces import PasswordManagerInterface
from settings.config import config
from settings.logging_config import get_logger

logger = get_logger(__name__, "accounts")


class PasswordService(PasswordServiceInterface):
    """Service for resetting and changing passwords"""

    def __init__(
            self,
            user_repository: UserRepositoryInterface,
            token_repository: TokenRepositoryInterface,
            password_manager: PasswordManagerInterface,
            email_sender: EmailSenderInterface,
            transaction_manager: TransactionManagerInterface
    ):
        """
        Initialize the service

        Args:
            user_repository: Repository for user data operations
            token_repository: Repository for token operations
            password_manager: Manager for password hashing and verification
            email_sender: Email sender for notifications
            transaction_manager: Manager owning transaction boundaries
        """
        self._user_repository = user_repository
        self._token_repository = token_repository
        self._password_manager = password_manager
        self._email_sender = email_sender
        self._transaction_manager = transaction_manager

    async def request_password_reset(self, request_data: PasswordResetRequestDTO) -> bool:
        """
        Request password reset by email

        Business logic: Replace any previous token in one transaction, so a failure
        cannot leave the user with neither the old link nor a new one, then send the
        email outside it. An unknown or inactive address is answered as success, so
        the endpoint does not reveal who is registered

        Args:
            request_data: Password reset request data containing email

        Returns:
            True if process completed

        Raises:
            PasswordResetError: If the reset token could not be replaced
            PasswordResetEmailError: If the email could not be sent
        """
        logger.info(f"Starting password reset request for email: {request_data.email}")

        user = await self._user_repository.get_user_by_email(request_data.email)

        if not user:
            logger.info(
                f"Password reset request for non-existent email: {request_data.email} (returning True for security)")
            return True

        if not user.is_active:
            logger.info(f"Password reset request for inactive user: {request_data.email} (returning True for security)")
            return True

        try:
            async with self._transaction_manager.atomic():
                await self._token_repository.delete_password_reset_tokens_by_user_id(user.id)
                logger.info(f"Deleted existing password reset tokens for user {user.id}")

                reset_token = await self._create_password_reset_token(user.id)
                logger.info(f"Password reset token created for user: {request_data.email}, user_id: {user.id}")
        except TokenCreationError as e:
            logger.error(
                f"Password reset not started for user {user.id}: the replacement token could not be created, "
                f"so the previous one was kept: {e}"
            )
            raise PasswordResetError("Password reset could not be started. Please try again.", e)

        try:
            await self._send_password_reset_email(request_data.email, reset_token)
            logger.info(f"Password reset email sent successfully to {request_data.email}")

            return True

        except BaseEmailError as e:
            logger.error(f"Failed to send password reset email to {request_data.email}: {e}")
            raise PasswordResetEmailError(
                f"Failed to send password reset email to {request_data.email}",
                original_error=e
            )

    async def confirm_password_reset(self, confirm_data: PasswordResetConfirmDTO) -> bool:
        """
        Confirm password reset using token and new password

        Args:
            confirm_data: Password reset confirmation data containing token and new password

        Returns:
            True if password was reset successfully

        Raises:
            InvalidPasswordResetTokenError: If token is invalid
            ExpiredPasswordResetTokenError: If token has expired
            PasswordResetTokenNotFoundError: If token not found
            UserPasswordError: If password processing fails
            PasswordResetError: If the new password could not be stored, or the used
                token could not be invalidated and the change was rolled back
        """
        logger.info(f"Starting password reset confirmation for token: {confirm_data.token[:10]}...")

        reset_token = await self._token_repository.get_password_reset_token_by_token(confirm_data.token)

        if not reset_token:
            logger.warning(f"Password reset token not found: {confirm_data.token[:10]}...")
            raise PasswordResetTokenNotFoundError("Password reset token not found or has been used")

        current_time = datetime.now(datetime_lib.UTC)
        if reset_token.expires_at <= current_time:
            logger.warning(f"Password reset token expired: {confirm_data.token[:10]}...")
            try:
                await self._token_repository.delete_password_reset_token(confirm_data.token)
            except Exception as e:
                logger.warning(f"Failed to delete expired password reset token: {e}")
            raise ExpiredPasswordResetTokenError("Password reset token has expired")

        user = await self._user_repository.get_user_by_id(reset_token.user_id)
        if not user:
            logger.error(f"User not found for password reset token: user_id={reset_token.user_id}")
            raise InvalidPasswordResetTokenError("Invalid password reset token")

        try:
            hashed_password = await self._password_manager.hash_password(confirm_data.new_password)
            logger.debug(f"New password hashed successfully for user: {user.email}")
        except (EmptyPasswordError, PasswordTooLongError, HashingError) as e:
            logger.error(f"Password hashing failed for user {user.email}: {e}")
            raise UserPasswordError(f"Password processing failed: {e}", e)

        async with self._transaction_manager.atomic():
            try:
                success = await self._user_repository.update_user_password(user.id, hashed_password)
                if not success:
                    logger.error(f"Failed to update password for user {user.id}")
                    raise PasswordResetError("Failed to update password")

                logger.info(f"Password updated successfully for user {user.id}")
            except UserUpdateError as e:
                logger.error(f"Failed to update password for user {user.id}: {e}")
                raise PasswordResetError(f"Failed to update password: {e}", e)

            revoked = await self._token_repository.delete_user_refresh_tokens(user.id)
            logger.info(f"Revoked {revoked} refresh tokens of user {user.id} after the password reset")

            try:
                await self._token_repository.delete_password_reset_token(confirm_data.token)
                logger.info(f"Password reset token deleted for user {user.id}")
            except TokenRepositoryError as e:
                logger.error(f"Failed to invalidate password reset token for user {user.id}: {e}")
                raise PasswordResetRollbackError(
                    "Password reset was rolled back: the used token could not be invalidated",
                    e
                )

        try:
            await self._send_password_reset_complete_email(user.email)
            logger.info(f"Password reset complete email sent to {user.email}")
        except BaseEmailError as e:
            logger.warning(f"Failed to send password reset complete email to {user.email}: {e}")

        logger.info(f"Password reset completed successfully for user: {user.email}")
        return True

    async def change_password(self, email: str, change_data: PasswordChangeDTO) -> None:
        """
        Change user password using email and password change data

        Args:
            email: User email from verified JWT token
            change_data: Password change data containing old and new passwords

        Returns:
            None - succeeds silently or raises exception

        Raises:
            UserNotFoundError: If user with given email is not found
            IncorrectCurrentPasswordError: If current password is incorrect
            SamePasswordError: If new password is the same as current password
            UserPasswordError: If password processing fails
            PasswordChangeError: If password change fails
        """
        logger.info(f"Starting password change process for user: {email}")

        user = await self._user_repository.get_user_by_email(email)
        if not user:
            logger.warning(f"User with email {email} not found")
            raise UserNotFoundError(f"User with email '{email}' not found")

        current_password_hash = await self._user_repository.get_hashed_password_by_email(email)
        if not current_password_hash:
            logger.error(f"Could not retrieve current password for user {email}")
            raise PasswordChangeError("Failed to retrieve current password")

        try:
            password_valid = await self._password_manager.verify_password(
                change_data.old_password, current_password_hash
            )
            if not password_valid:
                logger.warning(f"Password change failed: Incorrect current password for user {email}")
                raise IncorrectCurrentPasswordError("Current password is incorrect")
        except (EmptyPasswordError, VerificationError) as e:
            logger.error(f"Password verification failed for user {email}: {e}")
            raise IncorrectCurrentPasswordError("Current password is incorrect")

        try:
            same_password = await self._password_manager.verify_password(
                change_data.new_password, current_password_hash
            )
            if same_password:
                logger.warning(f"Password change failed: New password is the same as current for user {email}")
                raise SamePasswordError("New password must be different from current password")
        except (EmptyPasswordError, VerificationError):
            pass

        try:
            new_password_hash = await self._password_manager.hash_password(change_data.new_password)
            logger.debug(f"New password hashed successfully for user: {email}")
        except (EmptyPasswordError, PasswordTooLongError, HashingError) as e:
            logger.error(f"Password hashing failed for user {email}: {e}")
            raise UserPasswordError(f"Password processing failed: {e}", e)

        async with self._transaction_manager.atomic():
            try:
                success = await self._user_repository.update_user_password(user.id, new_password_hash)
                if not success:
                    logger.error(f"Failed to update password for user {user.id}")
                    raise PasswordChangeError("Failed to update password")

                logger.info(f"Password changed successfully for user {user.id}")
            except UserUpdateError as e:
                logger.error(f"Failed to update password for user {user.id}: {e}")
                raise PasswordChangeError(f"Failed to update password: {e}", e)

            revoked = await self._token_repository.delete_user_refresh_tokens(user.id)
            logger.info(f"Revoked {revoked} refresh tokens of user {user.id} after the password change")

        try:
            await self._send_password_change_notification_email(email)
            logger.info(f"Password change notification email sent to {email}")
        except BaseEmailError as e:
            logger.warning(f"Failed to send password change notification email to {email}: {e}")

        logger.info(f"Password change completed successfully for user: {email}")

    async def _create_password_reset_token(self, user_id: int) -> str:
        """
        Create password reset token for user

        Args:
            user_id: ID of the user to create token for

        Returns:
            Generated password reset token string

        Raises:
            TokenCreationError: If token creation fails
        """
        token = secrets.token_urlsafe(32)

        expires_at = datetime.now(datetime_lib.UTC) + timedelta(days=config.PASSWORD_TOKEN_VALID_DAYS)

        token_data = CreateTokenDTO(
            token=token,
            expires_at=expires_at,
            user_id=user_id
        )

        logger.debug(f"Creating password reset token for user {user_id}, expires at: {expires_at}")

        try:
            await self._token_repository.create_password_reset_token(token_data)
            logger.debug(f"Password reset token created successfully for user {user_id}")
            return token
        except TokenRepositoryError as e:
            logger.error(f"Failed to create password reset token for user {user_id}: {e}")
            raise TokenCreationError(f"Failed to create password reset token for user {user_id}", e)

    async def _send_password_reset_email(self, email: str, token: str) -> None:
        """
        Send password reset email to user

        Args:
            email: User's email address
            token: Password reset token

        Raises:
            BaseEmailError: If email sending fails
        """
        reset_link = config.build_frontend_url('/accounts/reset-password/confirm', token=token)

        logger.info(f"Sending password reset email to {email}")

        try:
            await self._email_sender.send_password_reset_email(email, reset_link)
            logger.info(f"Password reset email sent successfully to {email}")
        except BaseEmailError as e:
            logger.error(f"Failed to send password reset email to {email}: {e}")
            raise

    async def _send_password_reset_complete_email(self, email: str) -> None:
        """
        Send password reset complete email to user

        Args:
            email: User's email address

        Raises:
            BaseEmailError: If email sending fails
        """
        login_link = config.build_frontend_url('/accounts/login')

        logger.info(f"Sending password reset complete email to {email}")

        try:
            await self._email_sender.send_password_reset_complete_email(email, login_link)
            logger.info(f"Password reset complete email sent successfully to {email}")
        except BaseEmailError as e:
            logger.error(f"Failed to send password reset complete email to {email}: {e}")
            raise

    async def _send_password_change_notification_email(self, email: str) -> None:
        """
        Send password change notification email to user

        Args:
            email: User's email address

        Raises:
            BaseEmailError: If email sending fails
        """
        login_link = config.build_frontend_url('/accounts/login')
        change_time = datetime.now(datetime_lib.UTC).strftime("%Y-%m-%d %H:%M:%S UTC")

        logger.info(f"Sending password change notification email to {email}")

        try:
            await self._email_sender.send_password_change_notification_email(email, login_link, change_time)
            logger.info(f"Password change notification email sent successfully to {email}")
        except BaseEmailError as e:
            logger.error(f"Failed to send password change notification email to {email}: {e}")
            raise
