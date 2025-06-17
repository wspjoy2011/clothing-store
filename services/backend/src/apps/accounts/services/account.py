"""Account service implementation"""

import secrets
import datetime as datetime_lib
from datetime import datetime, timedelta

from apps.accounts.dto.users import UserDTO, CreateUserDTO
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
    ExpiredActivationTokenError
)
from apps.accounts.repositories.exceptions import (
    UserCreationError as RepoUserCreationError,
    TokenCreationError,
    TokenRepositoryError,
    UserUpdateError
)
from db.transaction_context import atomic
from security.interfaces import PasswordManagerInterface
from security.exceptions import EmptyPasswordError, PasswordTooLongError, HashingError
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
            email_sender: EmailSenderInterface
    ):
        """
        Initialize account service

        Args:
            user_repository: Repository for user data operations
            user_group_repository: Repository for user group operations
            token_repository: Repository for token operations
            password_manager: Manager for password hashing and verification
            email_sender: Email sender for notifications
        """
        self._user_repository = user_repository
        self._user_group_repository = user_group_repository
        self._token_repository = token_repository
        self._password_manager = password_manager
        self._email_sender = email_sender

    @atomic(['_user_repository', '_user_group_repository', '_token_repository'])
    async def register_user(self, user_data: CreateUserDTO) -> UserDTO:
        """
        Register a new user with default group assignment and create activation token

        Args:
            user_data: User registration data with plain text password (no group_id)

        Returns:
            Created UserDTO with hashed password and assigned group

        Raises:
            EmailAlreadyExistsError: If email already exists
            UserCreationError: If user creation fails at service level or default group not found
            UserPasswordError: Password processing errors
        """
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

        try:
            hashed_password = self._password_manager.hash_password(user_data.password)
            logger.debug(f"Password hashed successfully for user: {user_data.email}")
        except (EmptyPasswordError, PasswordTooLongError, HashingError) as e:
            logger.error(f"Password hashing failed for user {user_data.email}: {e}")
            raise UserPasswordError(f"Password processing failed: {e}", e)

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

            await self._send_activation_email(user_data.email, activation_token)
        except TokenCreationError as e:
            logger.error(f"Failed to create activation token for user {created_user.id}: {e}")
        except BaseEmailError as e:
            logger.error(f"Failed to send activation email to {user_data.email}: {e}")

        return created_user

    @atomic(['_user_repository', '_token_repository'])
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
