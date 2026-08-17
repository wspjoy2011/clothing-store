import secrets
import datetime as datetime_lib
from datetime import datetime, timedelta

from apps.accounts.dto.password_reset import (
    PasswordResetConfirmDTO,
    PasswordResetRequestDTO,
    PasswordChangeDTO
)
from apps.accounts.dto.users import (
    UserDTO,
    CreateUserDTO,
    UserLoginDTO,
    LoginResponseDTO
)
from apps.accounts.dto.tokens import CreateTokenDTO
from apps.accounts.dto.activation import ActivateAccountDTO
from apps.accounts.enums.user_groups import UserGroupEnum
from apps.accounts.interfaces.repositories import (
    UserRepositoryInterface,
    UserGroupRepositoryInterface,
    TokenRepositoryInterface
)
from apps.accounts.interfaces.services import AccountServiceInterface
from apps.accounts.services.exceptions import (
    EmailAlreadyExistsError,
    UserCreationError,
    UserPasswordError,
    UserNotFoundError,
    UserAlreadyActivatedError,
    InvalidActivationTokenError,
    ExpiredActivationTokenError,
    InvalidCredentialsError,
    UserInactiveError,
    LoginError,
    TokenGenerationError,
    InvalidRefreshTokenError,
    TokenValidationError,
    PasswordResetError,
    InvalidPasswordResetTokenError,
    ExpiredPasswordResetTokenError,
    PasswordResetTokenNotFoundError,
    PasswordResetEmailError,
    PasswordResetRollbackError,
    IncorrectCurrentPasswordError,
    SamePasswordError,
    PasswordChangeError
)
from apps.accounts.repositories.exceptions import (
    UserCreationError as RepoUserCreationError,
    TokenCreationError,
    TokenRepositoryError,
    UserUpdateError
)
from db.interfaces import TransactionManagerInterface
from security.interfaces import PasswordManagerInterface, JWTManagerInterface
from security.exceptions import (
    EmptyPasswordError,
    PasswordTooLongError,
    HashingError,
    VerificationError,
    TokenCreationError as SecurityTokenCreationError,
    InvalidTokenError,
    ExpiredTokenError, TokenSignatureError, InvalidTokenTypeError, EmptyTokenError
)
from notifications.email.interfaces import EmailSenderInterface
from notifications.exceptions.email import BaseEmailError
from settings.config import config
from settings.logging_config import get_logger

logger = get_logger(__name__, "accounts")


class AccountService(AccountServiceInterface):
    """Service for account management operations"""

    def __init__(
            self,
            user_repository: UserRepositoryInterface,
            user_group_repository: UserGroupRepositoryInterface,
            token_repository: TokenRepositoryInterface,
            password_manager: PasswordManagerInterface,
            jwt_manager: JWTManagerInterface,
            email_sender: EmailSenderInterface,
            transaction_manager: TransactionManagerInterface
    ):
        """
        Initialize account service

        Args:
            user_repository: Repository for user data operations
            user_group_repository: Repository for user group operations
            token_repository: Repository for token operations
            password_manager: Manager for password hashing and verification
            jwt_manager: Manager for JWT token operations
            email_sender: Email sender for notifications
            transaction_manager: Manager owning transaction boundaries
        """
        self._user_repository = user_repository
        self._user_group_repository = user_group_repository
        self._token_repository = token_repository
        self._password_manager = password_manager
        self._jwt_manager = jwt_manager
        self._email_sender = email_sender
        self._transaction_manager = transaction_manager

    async def register_user(self, user_data: CreateUserDTO) -> UserDTO:
        """
        Register a new user with default group assignment and create activation token

        Args:
            user_data: User registration data with plain text password (no group_id)

        Returns:
            Created UserDTO with hashed password and assigned group

        Raises:
            EmailAlreadyExistsError: If email already exists
            UserCreationError: If user creation fails, the default group is missing,
                or the activation token could not be created
            UserPasswordError: Password processing errors
        """
        try:
            hashed_password = await self._password_manager.hash_password(user_data.password)
            logger.debug(f"Password hashed successfully for user: {user_data.email}")
        except (EmptyPasswordError, PasswordTooLongError, HashingError) as e:
            logger.error(f"Password hashing failed for user {user_data.email}: {e}")
            raise UserPasswordError(f"Password processing failed: {e}", e)

        async with self._transaction_manager.atomic():
            existing_user = await self._user_repository.get_user_by_email(user_data.email)
            if existing_user:
                logger.warning(f"Registration failed: User with email {user_data.email} already exists")
                raise EmailAlreadyExistsError(f"User with email '{user_data.email}' already exists")

            default_group_name = UserGroupEnum.get_default_group()
            default_group = await self._user_group_repository.get_group_by_name(default_group_name)
            if not default_group:
                logger.error("Default group 'user' not found in database")
                raise UserCreationError("Default user group 'user' not found. Please contact administrator.")

            logger.debug(f"Default group found: ID={default_group.id}, name='{default_group.name}'")

            user_data_with_hash = CreateUserDTO(
                email=user_data.email,
                password=hashed_password,
                group_id=default_group.id
            )

            logger.debug(f"Creating user in repository: {user_data.email}")
            try:
                created_user = await self._user_repository.create_user(user_data_with_hash)
                logger.info(
                    f"User registration successful for email: {user_data.email}, user_id: {created_user.id},"
                    f" group: {default_group.name}")
            except RepoUserCreationError as e:
                logger.error(f"Repository user creation failed for {user_data.email}: {e}")
                raise UserCreationError(f"Failed to create user: {e}", e)

            try:
                activation_token = await self._create_activation_token(created_user.id)
                logger.info(f"Activation token created for user: {user_data.email}, user_id: {created_user.id}")
            except TokenCreationError as e:
                logger.error(
                    f"Registration rolled back for {user_data.email}: "
                    f"activation token could not be created for user {created_user.id}: {e}"
                )
                raise UserCreationError("Registration could not be completed. Please try again.", e)

        try:
            await self._send_activation_email(user_data.email, activation_token)
        except BaseEmailError as e:
            logger.error(f"Failed to send activation email to {user_data.email}: {e}")

        return created_user

    async def activate_account(self, activation_data: ActivateAccountDTO) -> UserDTO:
        """
        Activate user account using email and activation token

        Args:
            activation_data: Activation data containing email and token

        Returns:
            Activated UserDTO

        Raises:
            UserNotFoundError: If user with given email is not found
            UserAlreadyActivatedError: If user is already activated
            InvalidActivationTokenError: If token doesn't match the user
            ExpiredActivationTokenError: If activation token has expired
        """
        logger.info(f"Starting account activation for email: {activation_data.email}")

        async with self._transaction_manager.atomic():
            user = await self._user_repository.get_user_by_email(activation_data.email)
            if not user:
                logger.warning(f"Activation failed: User with email {activation_data.email} not found")
                raise UserNotFoundError(f"User with email '{activation_data.email}' not found")

            if user.is_active:
                logger.warning(f"Activation failed: User with email {activation_data.email} is already activated")
                raise UserAlreadyActivatedError(f"User with email '{activation_data.email}' is already activated")

            activation_token = await self._token_repository.get_activation_token_by_email_and_token(
                activation_data.email, activation_data.token
            )

            if not activation_token:
                logger.warning(f"Activation failed: Invalid token combination for email {activation_data.email}")
                raise InvalidActivationTokenError("Invalid email and token combination")

            current_time = datetime.now(datetime_lib.UTC)
            if activation_token.expires_at <= current_time:
                logger.warning(f"Activation failed: Token expired for email {activation_data.email}")
                raise ExpiredActivationTokenError("Activation token has expired")

            try:
                success = await self._user_repository.update_user_status(user.id, True)
                if not success:
                    logger.error(f"Failed to update user status for user {user.id}")
                    raise UserCreationError("Failed to activate user account")

                logger.info(f"User {user.id} activated successfully")
            except UserUpdateError as e:
                logger.error(f"Failed to update user status for user {user.id}: {e}")
                raise UserCreationError(f"Failed to activate user account: {e}", e)

            try:
                await self._token_repository.delete_activation_token(activation_data.token)
                logger.info(f"Activation token deleted for user {user.id}")
            except Exception as e:
                logger.warning(f"Failed to delete activation token for user {user.id}: {e}")

        try:
            await self._send_activation_complete_email(activation_data.email)
            logger.info(f"Activation complete email sent to {activation_data.email}")
        except BaseEmailError as e:
            logger.warning(f"Failed to send activation complete email to {activation_data.email}: {e}")

        updated_user = await self._user_repository.get_user_by_email(activation_data.email)
        if not updated_user:
            logger.error(f"Could not retrieve updated user data for {activation_data.email}")
            raise UserCreationError("Failed to retrieve updated user data")

        logger.info(f"Account activation completed successfully for email: {activation_data.email}")
        return updated_user

    async def resend_activation_email(self, email: str) -> bool:
        """
        Resend activation email for existing user

        Deletes any existing activation tokens and creates a new one

        Args:
            email: User email address

        Returns:
            True if email was sent successfully

        Raises:
            UserNotFoundError: If user with given email is not found
            UserAlreadyActivatedError: If user is already activated
            TokenCreationError: If token creation fails
            BaseEmailError: If email sending fails
        """
        logger.info(f"Starting resend activation email for: {email}")

        async with self._transaction_manager.atomic():
            user = await self._user_repository.get_user_by_email(email)
            if not user:
                logger.warning(f"Resend activation failed: User with email {email} not found")
                raise UserNotFoundError(f"User with email '{email}' not found")

            if user.is_active:
                logger.warning(f"Resend activation failed: User with email {email} is already activated")
                raise UserAlreadyActivatedError(f"User with email '{email}' is already activated")

            try:
                await self._token_repository.delete_activation_tokens_by_user_id(user.id)
                logger.info(f"Deleted existing activation tokens for user {user.id}")

                activation_token = await self._create_activation_token(user.id)
                logger.info(f"New activation token created for user: {email}, user_id: {user.id}")
            except TokenCreationError as e:
                logger.error(f"Failed to create activation token for user {user.id}: {e}")
                raise

        try:
            await self._send_resend_activation_email(email, activation_token)
            logger.info(f"Resend activation email sent successfully to {email}")

            return True
        except BaseEmailError as e:
            logger.error(f"Failed to send resend activation email to {email}: {e}")
            raise

    async def login_user(self, login_data: UserLoginDTO) -> LoginResponseDTO:
        """
        Authenticate user and generate JWT tokens

        Args:
            login_data: User login credentials (email and password)

        Returns:
            LoginResponseDTO with access and refresh tokens

        Raises:
            UserNotFoundError: If user with given email is not found
            UserInactiveError: If user account is not activated
            InvalidCredentialsError: If password is incorrect
            TokenGenerationError: If JWT token generation fails
            LoginError: If login fails for other reasons
        """
        logger.info(f"Starting login process for email: {login_data.email}")

        user = await self._user_repository.get_user_by_email(login_data.email)
        if not user:
            logger.warning(f"Login failed: User with email {login_data.email} not found")
            raise UserNotFoundError(f"User with email '{login_data.email}' not found")

        if not user.is_active:
            logger.warning(f"Login failed: User with email {login_data.email} is not activated")
            raise UserInactiveError(f"User account with email '{login_data.email}' is not activated")

        hashed_password = await self._user_repository.get_hashed_password_by_email(login_data.email)
        if not hashed_password:
            logger.error(f"Login failed: Could not retrieve password for email {login_data.email}")
            raise InvalidCredentialsError("Invalid email or password")

        try:
            password_valid = await self._password_manager.verify_password(login_data.password, hashed_password)
            if not password_valid:
                logger.warning(f"Login failed: Invalid password for email {login_data.email}")
                raise InvalidCredentialsError("Invalid email or password")
        except (EmptyPasswordError, VerificationError) as e:
            logger.error(f"Password verification failed for user {login_data.email}: {e}")
            raise InvalidCredentialsError("Invalid email or password")

        token_payload = {
            "user_id": user.id,
            "email": user.email,
            "group_id": user.group_id,
            "group_name": user.group_name
        }

        try:
            access_token = self._jwt_manager.create_access_token(token_payload)
            refresh_token = self._jwt_manager.create_refresh_token(token_payload)

            logger.info(f"JWT tokens generated successfully for user: {login_data.email}, user_id: {user.id}")

            await self._store_refresh_token(user.id, refresh_token)

        except SecurityTokenCreationError as e:
            logger.error(f"JWT token generation failed for user {user.id}: {e}")
            raise TokenGenerationError(f"Failed to generate authentication tokens: {e}", e)
        except Exception as e:
            logger.error(f"Unexpected error during login for user {user.id}: {e}")
            raise LoginError(f"Login failed due to unexpected error: {e}", e)
        else:
            return LoginResponseDTO(
                access_token=access_token,
                refresh_token=refresh_token
            )

    async def logout_user(self, refresh_token: str) -> None:
        """
        Logout user by removing refresh token from database

        Args:
            refresh_token: Refresh token to be removed

        Returns:
            None - always succeeds, no exceptions raised even if token doesn't exist
        """
        logger.info("Starting user logout process")

        try:
            await self._token_repository.delete_refresh_token(refresh_token)
            logger.info("Logout completed successfully")
        except Exception as e:
            logger.warning(f"Error during logout (ignored): {e}")

        return None

    async def get_user_by_refresh_token(self, refresh_token: str) -> UserDTO:
        """
        Get user information by refresh token

        Args:
            refresh_token: Valid refresh token

        Returns:
            UserDTO with user information

        Raises:
            InvalidRefreshTokenError: If refresh token is invalid or expired
            UserNotFoundError: If user associated with token is not found
            TokenValidationError: If token validation fails
        """
        logger.info("Starting get user by refresh token process")

        try:
            token_payload = self._jwt_manager.verify_refresh_token(refresh_token)
            logger.debug(f"Refresh token verified successfully for email: {token_payload.get('email')}")
        except Exception as e:
            logger.warning(f"Invalid refresh token provided: {e}")
            raise InvalidRefreshTokenError("Invalid or expired refresh token")

        stored_token = await self._token_repository.get_refresh_token_by_token(refresh_token)
        if not stored_token:
            logger.warning("Refresh token not found in database")
            raise InvalidRefreshTokenError("Refresh token not found or has been revoked")

        current_time = datetime.now(datetime_lib.UTC)
        if stored_token.expires_at <= current_time:
            logger.warning("Refresh token has expired")
            try:
                await self._token_repository.delete_refresh_token(refresh_token)
            except Exception as e:
                logger.warning(f"Failed to delete expired token: {e}")
            raise InvalidRefreshTokenError("Refresh token has expired")

        user_email = token_payload.get('email')
        if not user_email:
            logger.error("Email not found in refresh token payload")
            raise TokenValidationError("Invalid token payload: missing email")

        user = await self._user_repository.get_user_by_email(user_email)
        if not user:
            logger.warning(f"User with email {user_email} not found")
            raise UserNotFoundError(f"User with email '{user_email}' not found")

        logger.info(f"User retrieved successfully by refresh token for email: {user_email}")
        return user

    async def request_password_reset(self, request_data: PasswordResetRequestDTO) -> bool:
        """
        Request password reset by email

        Sends reset email if user exists (security - always returns True)

        Args:
            request_data: Password reset request data containing email

        Returns:
            True if process completed (always returns True for security)

        Raises:
            BaseEmailError: If email sending fails (only for existing users)
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
            await self._token_repository.delete_password_reset_tokens_by_user_id(user.id)
            logger.info(f"Deleted existing password reset tokens for user {user.id}")

            reset_token = await self._create_password_reset_token(user.id)
            logger.info(f"Password reset token created for user: {request_data.email}, user_id: {user.id}")

            await self._send_password_reset_email(request_data.email, reset_token)
            logger.info(f"Password reset email sent successfully to {request_data.email}")

            return True

        except TokenCreationError as e:
            logger.error(f"Failed to create password reset token for user {user.id}: {e}")
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
            password_valid = await self._password_manager.verify_password(change_data.old_password, current_password_hash)
            if not password_valid:
                logger.warning(f"Password change failed: Incorrect current password for user {email}")
                raise IncorrectCurrentPasswordError("Current password is incorrect")
        except (EmptyPasswordError, VerificationError) as e:
            logger.error(f"Password verification failed for user {email}: {e}")
            raise IncorrectCurrentPasswordError("Current password is incorrect")

        try:
            same_password = await self._password_manager.verify_password(change_data.new_password, current_password_hash)
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

        try:
            await self._send_password_change_notification_email(email)
            logger.info(f"Password change notification email sent to {email}")
        except BaseEmailError as e:
            logger.warning(f"Failed to send password change notification email to {email}: {e}")

        logger.info(f"Password change completed successfully for user: {email}")

    async def refresh_access_token(self, refresh_token: str) -> str:
        """
        Refresh access token using refresh token

        Args:
            refresh_token: Valid refresh token

        Returns:
            New access token string

        Raises:
            InvalidRefreshTokenError: If refresh token is invalid, expired, or not found in database
            UserNotFoundError: If user associated with token is not found
            TokenValidationError: If token validation fails
            TokenGenerationError: If new access token generation fails
        """
        logger.info("Starting access token refresh")

        try:
            payload = self._jwt_manager.verify_refresh_token(refresh_token)
            user_id = payload.get("user_id")

            if not user_id:
                logger.warning("Refresh token payload missing user_id")
                raise InvalidRefreshTokenError("Invalid refresh token payload")

            logger.debug(f"Refresh token payload verified for user_id: {user_id}")
        except (ExpiredTokenError, InvalidTokenError, TokenSignatureError,
                InvalidTokenTypeError, EmptyTokenError) as e:
            logger.warning(f"Refresh token verification failed: {e}")
            raise InvalidRefreshTokenError(f"Invalid refresh token: {str(e)}", e)
        except Exception as e:
            logger.error(f"Unexpected error during refresh token verification: {e}")
            raise TokenValidationError(f"Token validation failed: {str(e)}", e)

        try:
            stored_token = await self._token_repository.get_refresh_token_by_token(refresh_token)
            if not stored_token:
                logger.warning(f"Refresh token not found in database for user_id: {user_id}")
                raise InvalidRefreshTokenError("Refresh token not found or expired")

            logger.debug(f"Refresh token found in database for user_id: {user_id}")
        except Exception as e:
            logger.error(f"Error checking refresh token in database: {e}")
            raise TokenValidationError(f"Failed to validate refresh token: {str(e)}", e)

        try:
            user = await self._user_repository.get_user_by_id(user_id)
            if not user:
                logger.warning(f"User not found for user_id: {user_id}")
                raise UserNotFoundError(f"User with ID {user_id} not found")

            logger.debug(f"User found for token refresh: {user.email}")
        except Exception as e:
            logger.error(f"Error getting user for token refresh: {e}")
            raise UserNotFoundError(f"Failed to get user data: {str(e)}", e)

        try:
            token_payload = {
                "user_id": user.id,
                "email": user.email,
                "group_id": user.group_id,
                "group_name": user.group_name
            }

            new_access_token = self._jwt_manager.create_access_token(token_payload)
            logger.info(f"New access token created for user: {user.email}")

            return new_access_token

        except SecurityTokenCreationError as e:
            logger.error(f"Failed to create new access token for user {user.id}: {e}")
            raise TokenGenerationError(f"Failed to generate new access token: {str(e)}", e)
        except Exception as e:
            logger.error(f"Unexpected error creating access token for user {user.id}: {e}")
            raise TokenGenerationError(f"Token generation failed: {str(e)}", e)

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

    async def _store_refresh_token(self, user_id: int, refresh_token: str) -> None:
        """
        Store refresh token in database

        Args:
            user_id: ID of the user
            refresh_token: JWT refresh token to store

        Raises:
            TokenCreationError: If token storage fails
        """
        try:
            expiration = self._jwt_manager.get_token_expiration(refresh_token)

            token_data = CreateTokenDTO(
                token=refresh_token,
                expires_at=expiration,
                user_id=user_id
            )

            await self._token_repository.create_refresh_token(token_data)
            logger.debug(f"Refresh token stored successfully for user {user_id}")

        except Exception as e:
            logger.error(f"Failed to store refresh token for user {user_id}: {e}")
            raise TokenCreationError(f"Failed to store refresh token for user {user_id}", e)

    async def _create_activation_token(self, user_id: int) -> str:
        """
        Create activation token for user

        Args:
            user_id: ID of the user to create token for

        Returns:
            Generated activation token string

        Raises:
            TokenCreationError: If token creation fails
        """
        token = secrets.token_urlsafe(32)

        expires_at = datetime.now(datetime_lib.UTC) + timedelta(days=config.ACTIVATION_TOKEN_VALID_DAYS)

        token_data = CreateTokenDTO(
            token=token,
            expires_at=expires_at,
            user_id=user_id
        )

        logger.debug(f"Creating activation token for user {user_id}, expires at: {expires_at}")

        try:
            await self._token_repository.create_activation_token(token_data)
            logger.debug(f"Activation token created successfully for user {user_id}")
            return token
        except TokenRepositoryError as e:
            logger.error(f"Failed to create activation token for user {user_id}: {e}")
            raise TokenCreationError(f"Failed to create activation token for user {user_id}", e)

    async def _send_activation_email(self, email: str, token: str) -> None:
        """
        Send activation email to user

        Args:
            email: User's email address
            token: Activation token

        Raises:
            BaseEmailError: If email sending fails
        """
        activation_link = config.build_frontend_url('/accounts/activate', token=token, email=email)

        logger.info(f"Sending activation email to {email}")

        try:
            await self._email_sender.send_activation_email(email, activation_link)
            logger.info(f"Activation email sent successfully to {email}")
        except BaseEmailError as e:
            logger.error(f"Failed to send activation email to {email}: {e}")
            raise

    async def _send_resend_activation_email(self, email: str, token: str) -> None:
        """
        Send resend activation email to user

        Args:
            email: User's email address
            token: Activation token

        Raises:
            BaseEmailError: If email sending fails
        """
        activation_link = config.build_frontend_url('/accounts/activate', token=token, email=email)

        logger.info(f"Sending resend activation email to {email}")

        try:
            await self._email_sender.send_resend_activation_email(email, activation_link)
            logger.info(f"Resend activation email sent successfully to {email}")
        except BaseEmailError as e:
            logger.error(f"Failed to send resend activation email to {email}: {e}")
            raise

    async def _send_activation_complete_email(self, email: str) -> None:
        """
        Send activation complete email to user

        Args:
            email: User's email address

        Raises:
            BaseEmailError: If email sending fails
        """
        login_link = config.build_frontend_url('/accounts/login')

        logger.info(f"Sending activation complete email to {email}")

        try:
            await self._email_sender.send_activation_complete_email(email, login_link)
            logger.info(f"Activation complete email sent successfully to {email}")
        except BaseEmailError as e:
            logger.error(f"Failed to send activation complete email to {email}: {e}")
            raise
