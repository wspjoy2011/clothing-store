"""Account service implementation"""

from apps.accounts.dto.users import UserDTO, CreateUserDTO
from apps.accounts.enums.user_groups import UserGroupEnum
from apps.accounts.interfaces.repositories import UserRepositoryInterface, UserGroupRepositoryInterface
from apps.accounts.interfaces.services import AccountServiceInterface
from apps.accounts.services.exceptions import EmailAlreadyExistsError, UserCreationError, UserPasswordError
from apps.accounts.repositories.exceptions import UserCreationError as RepoUserCreationError
from security.interfaces import PasswordManagerInterface
from security.exceptions import EmptyPasswordError, PasswordTooLongError, HashingError
from settings.logging_config import get_logger

logger = get_logger(__name__, "accounts")


class AccountService(AccountServiceInterface):
    """Service for account management operations"""

    def __init__(
            self,
            user_repository: UserRepositoryInterface,
            user_group_repository: UserGroupRepositoryInterface,
            password_manager: PasswordManagerInterface
    ):
        """
        Initialize account service

        Args:
            user_repository: Repository for user data operations
            user_group_repository: Repository for user group operations
            password_manager: Manager for password hashing and verification
        """
        self._user_repository = user_repository
        self._user_group_repository = user_group_repository
        self._password_manager = password_manager

    async def register_user(self, user_data: CreateUserDTO) -> UserDTO:
        """
        Register a new user with default group assignment

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
            return created_user
        except RepoUserCreationError as e:
            logger.error(f"Repository user creation failed for {user_data.email}: {e}")
            raise UserCreationError(f"Failed to create user: {e}", e)
