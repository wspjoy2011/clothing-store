from typing import Optional, List

import psycopg

from apps.accounts.dto.users import UserDTO, UserWithProfileDTO, CreateUserDTO
from apps.accounts.interfaces.repositories import UserRepositoryInterface
from apps.accounts.repositories.exceptions import (
    UserCreationError,
    UserUpdateError,
    UserDeletionError
)
from apps.accounts.repositories.base import BaseRepository
from db.interfaces import DAOInterface, SQLQueryBuilderInterface
from settings.logging_config import get_logger

logger = get_logger(__name__, "accounts")


class UserRepository(BaseRepository, UserRepositoryInterface):
    """Repository implementation for user operations using SQL database"""

    def __init__(self, dao: DAOInterface, query_builder: SQLQueryBuilderInterface):
        super().__init__(dao, query_builder)

    async def get_user_by_id(self, user_id: int) -> Optional[UserDTO]:
        """Get a single user by ID"""
        self._build_user_query()
        self._query_builder.where("u.id = %s", user_id)

        result = await self._execute_query_single("Get user by ID")
        return self.map_to_user_dto(result) if result else None

    async def get_user_by_email(self, email: str) -> Optional[UserDTO]:
        """Get a single user by email"""
        self._build_user_query()
        self._query_builder.where("u.email = %s", email)

        result = await self._execute_query_single("Get user by email")
        return self.map_to_user_dto(result) if result else None

    async def get_user_with_profile_by_id(self, user_id: int) -> Optional[UserWithProfileDTO]:
        """Get a user with profile information by ID"""
        self._build_user_query(with_profile=True)
        self._query_builder.where("u.id = %s", user_id)

        result = await self._execute_query_single("Get user with profile by ID")
        return self.map_to_user_with_profile_dto(result) if result else None

    async def get_user_with_profile_by_email(self, email: str) -> Optional[UserWithProfileDTO]:
        """Get a user with profile information by email"""
        self._build_user_query(with_profile=True)
        self._query_builder.where("u.email = %s", email)

        result = await self._execute_query_single("Get user with profile by email")
        return self.map_to_user_with_profile_dto(result) if result else None

    async def create_user(self, user_data: CreateUserDTO) -> UserDTO:
        """Create a new user"""
        query = f"""
            INSERT INTO {self.APP_NAME}_users (email, hashed_password, group_id)
            VALUES (%s, %s, %s)
            RETURNING id, email, is_active, created_at, updated_at, group_id
        """

        params = [user_data.email, user_data.password, user_data.group_id]

        try:
            result = await self._execute_custom_query_single(query, params, "Create user")
        except Exception as e:
            if isinstance(e, (psycopg.Error, psycopg.DatabaseError, psycopg.IntegrityError)):
                raise UserCreationError(f"Failed to create user with email: {user_data.email}", e)
            raise UserCreationError(f"Unexpected error creating user with email: {user_data.email}", e)

        if not result:
            raise UserCreationError(f"No result returned when creating user with email: {user_data.email}")

        group_name = await self._get_group_name(result[5])
        return self.map_user_dto_with_group_name(result, group_name)

    async def update_user_status(self, user_id: int, is_active: bool) -> bool:
        """Update user active status"""
        query = f"UPDATE {self.APP_NAME}_users SET is_active = %s WHERE id = %s"
        params = [is_active, user_id]

        try:
            result = await self._execute_custom_query_single(query, params, "Update user status")
        except Exception as e:
            if isinstance(e, (psycopg.Error, psycopg.DatabaseError)):
                raise UserUpdateError(f"Failed to update status for user with ID: {user_id}", e)
            raise UserUpdateError(f"Unexpected error updating status for user with ID: {user_id}", e)

        return result is not None

    async def update_user_password(self, user_id: int, hashed_password: str) -> bool:
        """Update user password"""
        query = f"UPDATE {self.APP_NAME}_users SET hashed_password = %s WHERE id = %s"
        params = [hashed_password, user_id]

        try:
            result = await self._execute_custom_query_single(query, params, "Update user password")
        except Exception as e:
            if isinstance(e, (psycopg.Error, psycopg.DatabaseError)):
                raise UserUpdateError(f"Failed to update password for user with ID: {user_id}", e)
            raise UserUpdateError(f"Unexpected error updating password for user with ID: {user_id}", e)

        return result is not None

    async def delete_user(self, user_id: int) -> bool:
        """Delete a user"""
        query = f"DELETE FROM {self.APP_NAME}_users WHERE id = %s"
        params = [user_id]

        try:
            result = await self._execute_custom_query_single(query, params, "Delete user")
        except Exception as e:
            if isinstance(e, (psycopg.Error, psycopg.DatabaseError)):
                raise UserDeletionError(f"Failed to delete user with ID: {user_id}", e)
            raise UserDeletionError(f"Unexpected error deleting user with ID: {user_id}", e)

        return result is not None

    async def get_users_list(self, limit: int = 50, offset: int = 0) -> List[UserWithProfileDTO]:
        """Get list of users with pagination"""
        self._build_user_query(with_profile=True)
        self._query_builder.order_by("u.created_at DESC")
        self._query_builder.limit(limit).offset(offset)

        results = await self._execute_query_multiple("Get users list")
        return [self.map_to_user_with_profile_dto(row) for row in results]

    async def get_users_count(self) -> int:
        """Get total count of users"""
        self._query_builder.reset().select("COUNT(*)")
        return await self._execute_count_query("Get users count")

    def _build_user_query(self, with_profile: bool = False) -> None:
        """Build base user query with optional profile join"""
        if with_profile:
            self._query_builder.reset().select(
                "u.id", "u.email", "u.is_active", "u.created_at", "u.updated_at",
                "u.group_id", "g.name as group_name",
                "p.first_name", "p.last_name", "p.avatar", "p.gender",
                "p.date_of_birth", "p.info"
            )
            self._query_builder.join("LEFT JOIN accounts_user_groups g ON u.group_id = g.id")
            self._query_builder.join("LEFT JOIN accounts_user_profiles p ON u.id = p.user_id")
        else:
            self._query_builder.reset().select(
                "u.id", "u.email", "u.is_active", "u.created_at", "u.updated_at",
                "u.group_id", "g.name as group_name"
            ).from_table("accounts_users u")
            self._query_builder.join("LEFT JOIN accounts_user_groups g ON u.group_id = g.id")

    async def _get_group_name(self, group_id: int) -> Optional[str]:
        """Get group name by ID"""
        if not group_id:
            return None

        try:
            self._query_builder.reset().select("name").from_table("accounts_user_groups")
            self._query_builder.where("id = %s", group_id)

            query, params = self._query_builder.build()
            result = await self._dao.execute(query, params, fetch_one=True)
        except Exception as e:
            logger.warning(f"Error getting group name: {e}")
            return None

        return result[0] if result else None
