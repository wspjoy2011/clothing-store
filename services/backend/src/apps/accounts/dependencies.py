from fastapi import Depends

from apps.accounts.interfaces.repositories import (
    TokenRepositoryInterface,
    UserGroupRepositoryInterface,
    UserRepositoryInterface,
)
from apps.accounts.interfaces.services import (
    AuthenticationServiceInterface,
    PasswordServiceInterface,
    RegistrationServiceInterface,
)
from apps.accounts.repositories.token import TokenRepository
from apps.accounts.repositories.user import UserRepository
from apps.accounts.repositories.user_group import UserGroupRepository
from apps.accounts.services.authentication import AuthenticationService
from apps.accounts.services.password import PasswordService
from apps.accounts.services.registration import RegistrationService
from db.dependencies import get_database_dao, get_query_builder, get_transaction_manager
from db.interfaces import DAOInterface, SQLQueryBuilderInterface, TransactionManagerInterface
from notifications.dependencies import get_email_sender_dependency
from notifications.email.interfaces import EmailSenderInterface
from security.dependencies import get_jwt_manager, get_password_manager
from security.interfaces import JWTManagerInterface, PasswordManagerInterface


async def get_user_repository(
        dao: DAOInterface = Depends(get_database_dao),
        query_builder: SQLQueryBuilderInterface = Depends(lambda: get_query_builder("accounts_users"))
) -> UserRepositoryInterface:
    """
    Dependency for getting user repository.

    Args:
        dao: Data Access Object for database operations
        query_builder: SQL query builder for users table

    Returns:
        Initialized user repository
    """
    return UserRepository(dao, query_builder)


async def get_user_group_repository(
        dao: DAOInterface = Depends(get_database_dao),
        query_builder: SQLQueryBuilderInterface = Depends(lambda: get_query_builder("accounts_user_groups"))
) -> UserGroupRepositoryInterface:
    """
    Dependency for getting user group repository.

    Args:
        dao: Data Access Object for database operations
        query_builder: SQL query builder for user groups table

    Returns:
        Initialized user group repository
    """
    return UserGroupRepository(dao, query_builder)



async def get_token_repository(
        dao: DAOInterface = Depends(get_database_dao),
        query_builder: SQLQueryBuilderInterface = Depends(lambda: get_query_builder("accounts_users"))
) -> TokenRepositoryInterface:
    """
    Dependency for getting token repository.

    Args:
        dao: Data Access Object for database operations
        query_builder: SQL query builder for user profiles table

    Returns:
        Initialized token repository
    """
    return TokenRepository(dao, query_builder)


async def get_registration_service(
        user_repository: UserRepositoryInterface = Depends(get_user_repository),
        user_group_repository: UserGroupRepositoryInterface = Depends(get_user_group_repository),
        token_repository: TokenRepositoryInterface = Depends(get_token_repository),
        password_manager: PasswordManagerInterface = Depends(get_password_manager),
        email_sender: EmailSenderInterface = Depends(get_email_sender_dependency),
        transaction_manager: TransactionManagerInterface = Depends(get_transaction_manager)
) -> RegistrationServiceInterface:
    """
    Dependency for getting the registration service

    Args:
        user_repository: Repository for user data operations
        user_group_repository: Repository for user group operations
        token_repository: Repository for token operations
        password_manager: Manager for password hashing and verification
        email_sender: Email sender for notifications
        transaction_manager: Manager owning transaction boundaries

    Returns:
        Initialized registration service
    """
    return RegistrationService(
        user_repository=user_repository,
        user_group_repository=user_group_repository,
        token_repository=token_repository,
        password_manager=password_manager,
        email_sender=email_sender,
        transaction_manager=transaction_manager
    )


async def get_authentication_service(
        user_repository: UserRepositoryInterface = Depends(get_user_repository),
        token_repository: TokenRepositoryInterface = Depends(get_token_repository),
        password_manager: PasswordManagerInterface = Depends(get_password_manager),
        jwt_manager: JWTManagerInterface = Depends(get_jwt_manager),
        transaction_manager: TransactionManagerInterface = Depends(get_transaction_manager)
) -> AuthenticationServiceInterface:
    """
    Dependency for getting the authentication service

    Args:
        user_repository: Repository for user data operations
        token_repository: Repository for token operations
        password_manager: Manager for password hashing and verification
        jwt_manager: Manager for JWT token operations
        transaction_manager: Manager owning transaction boundaries

    Returns:
        Initialized authentication service
    """
    return AuthenticationService(
        user_repository=user_repository,
        token_repository=token_repository,
        password_manager=password_manager,
        jwt_manager=jwt_manager,
        transaction_manager=transaction_manager
    )


async def get_password_service(
        user_repository: UserRepositoryInterface = Depends(get_user_repository),
        token_repository: TokenRepositoryInterface = Depends(get_token_repository),
        password_manager: PasswordManagerInterface = Depends(get_password_manager),
        email_sender: EmailSenderInterface = Depends(get_email_sender_dependency),
        transaction_manager: TransactionManagerInterface = Depends(get_transaction_manager)
) -> PasswordServiceInterface:
    """
    Dependency for getting the password service

    Args:
        user_repository: Repository for user data operations
        token_repository: Repository for token operations
        password_manager: Manager for password hashing and verification
        email_sender: Email sender for notifications
        transaction_manager: Manager owning transaction boundaries

    Returns:
        Initialized password service
    """
    return PasswordService(
        user_repository=user_repository,
        token_repository=token_repository,
        password_manager=password_manager,
        email_sender=email_sender,
        transaction_manager=transaction_manager
    )
