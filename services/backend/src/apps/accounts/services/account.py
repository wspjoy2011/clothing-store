"""Account service implementation"""

import secrets
import datetime as datetime_lib
from datetime import datetime, timedelta

from apps.accounts.dto.users import UserDTO, CreateUserDTO
from apps.accounts.dto.tokens import CreateTokenDTO
from apps.accounts.enums.user_groups import UserGroupEnum
from apps.accounts.interfaces.repositories import (
    UserRepositoryInterface,
    UserGroupRepositoryInterface,
    TokenRepositoryInterface
)
from apps.accounts.interfaces.services import AccountServiceInterface
from apps.accounts.services.exceptions import EmailAlreadyExistsError, UserCreationError, UserPasswordError
from apps.accounts.repositories.exceptions import (
    UserCreationError as RepoUserCreationError,
    TokenCreationError,
    TokenRepositoryError
)
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
                f"User registration successful for email: {user_data.email}, user_id: {created_user.id}, group: {default_group.name}")
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
        activation_link = config.build_frontend_url('/accounts/activate', token=token)

        logger.info(f"Sending activation email to {email}")

        try:
            await self._email_sender.send_activation_email(email, activation_link)
            logger.info(f"Activation email sent successfully to {email}")
        except BaseEmailError as e:
            logger.error(f"Failed to send activation email to {email}: {e}")
            raise
