"""Account service implementation"""

import secrets
import datetime as datetime_lib
from datetime import datetime, timedelta

from apps.accounts.dto.users import UserDTO, CreateUserDTO, UserLoginDTO, LoginResponseDTO
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
    TokenGenerationError
)
from apps.accounts.repositories.exceptions import (
    UserCreationError as RepoUserCreationError,
    TokenCreationError,
    TokenRepositoryError,
    UserUpdateError
)
from db.transaction_context import atomic
from security.interfaces import PasswordManagerInterface, JWTManagerInterface
from security.exceptions import (
    EmptyPasswordError,
    PasswordTooLongError,
    HashingError,
    VerificationError,
    TokenCreationError as SecurityTokenCreationError
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
            email_sender: EmailSenderInterface
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
        """
        self._user_repository = user_repository
        self._user_group_repository = user_group_repository
        self._token_repository = token_repository
        self._password_manager = password_manager
        self._jwt_manager = jwt_manager
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

    @atomic(['_user_repository', '_token_repository'])
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

            await self._send_resend_activation_email(email, activation_token)
            logger.info(f"Resend activation email sent successfully to {email}")

            return True

        except TokenCreationError as e:
            logger.error(f"Failed to create activation token for user {user.id}: {e}")
            raise
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
            password_valid = self._password_manager.verify_password(login_data.password, hashed_password)
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
