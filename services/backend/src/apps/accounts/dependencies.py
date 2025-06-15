from fastapi import Depends

from apps.accounts.interfaces.repositories import (
    UserRepositoryInterface,
    UserGroupRepositoryInterface,
    UserProfileRepositoryInterface,
    TokenRepositoryInterface
)
from apps.accounts.interfaces.services import AccountServiceInterface
from apps.accounts.repositories.user import UserRepository
from apps.accounts.repositories.user_group import UserGroupRepository
from apps.accounts.repositories.user_profile import UserProfileRepository
from apps.accounts.repositories.token import TokenRepository
from apps.accounts.services.account import AccountService
from db.dependencies import get_database_dao, get_query_builder
from db.interfaces import DAOInterface, SQLQueryBuilderInterface
from notifications.dependencies import get_email_sender_dependency
from notifications.email.interfaces import EmailSenderInterface
from security.dependencies import get_password_manager
from security.interfaces import PasswordManagerInterface


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


async def get_user_profile_repository(
        dao: DAOInterface = Depends(get_database_dao),
        query_builder: SQLQueryBuilderInterface = Depends(lambda: get_query_builder("accounts_user_profiles"))
) -> UserProfileRepositoryInterface:
    """
    Dependency for getting user profile repository.

    Args:
        dao: Data Access Object for database operations
        query_builder: SQL query builder for user profiles table

    Returns:
        Initialized user profile repository
    """
    return UserProfileRepository(dao, query_builder)


async def get_token_repository(
        dao: DAOInterface = Depends(get_database_dao),
        query_builder: SQLQueryBuilderInterface = Depends(lambda: get_query_builder("accounts_users"))
)  -> TokenRepositoryInterface:
    """
    Dependency for getting token repository.

    Args:
        dao: Data Access Object for database operations
        query_builder: SQL query builder for user profiles table

    Returns:
        Initialized token repository
    """
    return TokenRepository(dao, query_builder)


async def get_account_service(
        user_repository: UserRepositoryInterface = Depends(get_user_repository),
        user_group_repository: UserGroupRepositoryInterface = Depends(get_user_group_repository),
        token_repository: TokenRepositoryInterface = Depends(get_token_repository),
        password_manager: PasswordManagerInterface = Depends(get_password_manager),
        email_sender: EmailSenderInterface = Depends(get_email_sender_dependency)
) -> AccountServiceInterface:
    """
    Dependency for getting account service.

    Args:
        user_repository: Repository for user data operations
        user_group_repository: Repository for user group operations
        token_repository: Repository for token operations
        password_manager: Manager for password hashing and verification
        email_sender: Email sender for notifications

    Returns:
        Initialized account service
    """
    return AccountService(
        user_repository=user_repository,
        user_group_repository=user_group_repository,
        token_repository=token_repository,
        password_manager=password_manager,
        email_sender=email_sender
    )
