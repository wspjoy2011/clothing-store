from typing import Optional

import psycopg

from apps.accounts.dto.users import UserProfileDTO
from apps.accounts.interfaces.repositories import UserProfileRepositoryInterface
from apps.accounts.repositories.exceptions import (
    ProfileCreationError,
    ProfileUpdateError,
    ProfileDeletionError
)
from apps.accounts.repositories.base import BaseRepository
from db.interfaces import DAOInterface, SQLQueryBuilderInterface
from settings.logging_config import get_logger

logger = get_logger(__name__, "accounts")


class UserProfileRepository(BaseRepository, UserProfileRepositoryInterface):
    """Repository implementation for user profile operations using SQL database"""

    def __init__(self, dao: DAOInterface, query_builder: SQLQueryBuilderInterface):
        super().__init__(dao, query_builder)

    async def get_profile_by_user_id(self, user_id: int) -> Optional[UserProfileDTO]:
        """Get user profile by user ID"""
        self._query_builder.reset().select(
            "id", "first_name", "last_name", "avatar", "gender", "date_of_birth", "info", "user_id"
        )
        self._query_builder.where("user_id = %s", user_id)

        result = await self._execute_query_single("Get profile by user ID")
        return self.map_to_profile_dto(result) if result else None

    async def create_profile(self, user_id: int, profile_data: dict) -> UserProfileDTO:
        """Create user profile"""
        insert_fields = ["first_name", "last_name", "avatar", "gender", "date_of_birth", "info", "user_id"]
        placeholders = ", ".join(["%s"] * len(insert_fields))

        query = f"""
            INSERT INTO {self.APP_NAME}_user_profiles 
            ({', '.join(insert_fields)})
            VALUES ({placeholders})
            RETURNING id, first_name, last_name, avatar, gender, date_of_birth, info, user_id
        """

        params = [
            profile_data.get('first_name'),
            profile_data.get('last_name'),
            profile_data.get('avatar'),
            profile_data.get('gender'),
            profile_data.get('date_of_birth'),
            profile_data.get('info'),
            user_id
        ]

        try:
            result = await self._execute_custom_query_single(query, params, "Create profile")
        except Exception as e:
            if isinstance(e, (psycopg.Error, psycopg.DatabaseError, psycopg.IntegrityError)):
                raise ProfileCreationError(f"Failed to create profile for user with ID: {user_id}", e)
            raise ProfileCreationError(f"Unexpected error creating profile for user with ID: {user_id}", e)

        if not result:
            raise ProfileCreationError(f"No result returned when creating profile for user: {user_id}")

        return self.map_to_profile_dto(result)

    async def update_profile(self, user_id: int, profile_data: dict) -> Optional[UserProfileDTO]:
        """Update user profile"""
        update_fields = []
        params = []

        for field in ['first_name', 'last_name', 'avatar', 'gender', 'date_of_birth', 'info']:
            if field in profile_data:
                update_fields.append(f"{field} = %s")
                params.append(profile_data[field])

        if not update_fields:
            return await self.get_profile_by_user_id(user_id)

        params.append(user_id)

        query = f"""
            UPDATE {self.APP_NAME}_user_profiles 
            SET {', '.join(update_fields)}
            WHERE user_id = %s
            RETURNING id, first_name, last_name, avatar, gender, date_of_birth, info, user_id
        """

        try:
            result = await self._execute_custom_query_single(query, params, "Update profile")
        except Exception as e:
            if isinstance(e, (psycopg.Error, psycopg.DatabaseError)):
                raise ProfileUpdateError(f"Failed to update profile for user with ID: {user_id}", e)
            raise ProfileUpdateError(f"Unexpected error updating profile for user with ID: {user_id}", e)

        return self.map_to_profile_dto(result) if result else None

    async def delete_profile(self, user_id: int) -> bool:
        """Delete user profile"""
        self._query_builder.reset()
        self._query_builder.where("user_id = %s", user_id)

        query, params = self._build_delete_query("user_profiles")

        try:
            result = await self._execute_custom_query_single(query, params, "Delete profile")
        except Exception as e:
            if isinstance(e, (psycopg.Error, psycopg.DatabaseError)):
                raise ProfileDeletionError(f"Failed to delete profile for user with ID: {user_id}", e)
            raise ProfileDeletionError(f"Unexpected error deleting profile for user with ID: {user_id}", e)

        return result is not None
