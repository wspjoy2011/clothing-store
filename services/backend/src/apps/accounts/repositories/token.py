from typing import Optional, List

import psycopg

from apps.accounts.dto.tokens import (
    ActivationTokenDTO,
    PasswordResetTokenDTO,
    RefreshTokenDTO,
    CreateTokenDTO
)
from apps.accounts.interfaces.repositories import TokenRepositoryInterface
from apps.accounts.repositories.exceptions import (
    TokenCreationError,
    TokenDeletionError
)
from apps.accounts.repositories.base import BaseRepository
from db.interfaces import DAOInterface, SQLQueryBuilderInterface
from settings.logging_config import get_logger

logger = get_logger(__name__, "accounts")


class TokenRepository(BaseRepository, TokenRepositoryInterface):
    """Repository implementation for token operations using SQL database"""

    def __init__(self, dao: DAOInterface, query_builder: SQLQueryBuilderInterface):
        super().__init__(dao, query_builder)

    async def get_activation_token_by_token(self, token: str) -> Optional[ActivationTokenDTO]:
        """Get activation token by token string"""
        self._build_activation_token_query()
        self._query_builder.where("token = %s AND expires_at > CURRENT_TIMESTAMP", token)

        result = await self._execute_query_single("Get activation token by token")
        return self.map_to_activation_token_dto(result) if result else None

    async def get_activation_token_by_user_id(self, user_id: int) -> Optional[ActivationTokenDTO]:
        """Get activation token by user ID"""
        self._build_activation_token_query()
        self._query_builder.where("user_id = %s AND expires_at > CURRENT_TIMESTAMP", user_id)

        result = await self._execute_query_single("Get activation token by user ID")
        return self.map_to_activation_token_dto(result) if result else None

    async def create_activation_token(self, token_data: CreateTokenDTO) -> ActivationTokenDTO:
        """Create activation token"""
        query = f"""
            INSERT INTO {self.APP_NAME}_activation_tokens (token, expires_at, user_id)
            VALUES (%s, %s, %s)
            ON CONFLICT (user_id) DO UPDATE SET 
                token = EXCLUDED.token,
                expires_at = EXCLUDED.expires_at
            RETURNING id, token, expires_at, user_id
        """

        params = [token_data.token, token_data.expires_at, token_data.user_id]

        try:
            result = await self._execute_custom_query_single(query, params, "Create activation token")
        except Exception as e:
            if isinstance(e, (psycopg.Error, psycopg.DatabaseError, psycopg.IntegrityError)):
                raise TokenCreationError(f"Failed to create activation token for user ID: {token_data.user_id}", e)
            raise TokenCreationError(f"Unexpected error creating activation token for user ID: {token_data.user_id}", e)

        if not result:
            raise TokenCreationError(
                f"No result returned when creating activation token for user: {token_data.user_id}")

        return self.map_to_activation_token_dto(result)

    async def delete_activation_token(self, token: str) -> bool:
        """Delete activation token"""
        query = f"DELETE FROM {self.APP_NAME}_activation_tokens WHERE token = %s"
        params = [token]

        try:
            result = await self._execute_custom_query_single(query, params, "Delete activation token")
        except Exception as e:
            if isinstance(e, (psycopg.Error, psycopg.DatabaseError)):
                raise TokenDeletionError(f"Failed to delete activation token: {token}", e)
            raise TokenDeletionError(f"Unexpected error deleting activation token: {token}", e)

        return result is not None

    async def get_password_reset_token_by_token(self, token: str) -> Optional[PasswordResetTokenDTO]:
        """Get password reset token by token string"""
        self._build_password_reset_token_query()
        self._query_builder.where("token = %s AND expires_at > CURRENT_TIMESTAMP", token)

        result = await self._execute_query_single("Get password reset token by token")
        return self.map_to_password_reset_token_dto(result) if result else None

    async def get_password_reset_token_by_user_id(self, user_id: int) -> Optional[PasswordResetTokenDTO]:
        """Get password reset token by user ID"""
        self._build_password_reset_token_query()
        self._query_builder.where("user_id = %s AND expires_at > CURRENT_TIMESTAMP", user_id)

        result = await self._execute_query_single("Get password reset token by user ID")
        return self.map_to_password_reset_token_dto(result) if result else None

    async def create_password_reset_token(self, token_data: CreateTokenDTO) -> PasswordResetTokenDTO:
        """Create password reset token"""
        query = f"""
            INSERT INTO {self.APP_NAME}_password_reset_tokens (token, expires_at, user_id)
            VALUES (%s, %s, %s)
            ON CONFLICT (user_id) DO UPDATE SET 
                token = EXCLUDED.token,
                expires_at = EXCLUDED.expires_at
            RETURNING id, token, expires_at, user_id
        """

        params = [token_data.token, token_data.expires_at, token_data.user_id]

        try:
            result = await self._execute_custom_query_single(query, params, "Create password reset token")
        except Exception as e:
            if isinstance(e, (psycopg.Error, psycopg.DatabaseError, psycopg.IntegrityError)):
                raise TokenCreationError(f"Failed to create password reset token for user ID: {token_data.user_id}", e)
            raise TokenCreationError(
                f"Unexpected error creating password reset token for user ID: {token_data.user_id}", e)

        if not result:
            raise TokenCreationError(
                f"No result returned when creating password reset token for user: {token_data.user_id}")

        return self.map_to_password_reset_token_dto(result)

    async def delete_password_reset_token(self, token: str) -> bool:
        """Delete password reset token"""
        query = f"DELETE FROM {self.APP_NAME}_password_reset_tokens WHERE token = %s"
        params = [token]

        try:
            result = await self._execute_custom_query_single(query, params, "Delete password reset token")
        except Exception as e:
            if isinstance(e, (psycopg.Error, psycopg.DatabaseError)):
                raise TokenDeletionError(f"Failed to delete password reset token: {token}", e)
            raise TokenDeletionError(f"Unexpected error deleting password reset token: {token}", e)

        return result is not None

    async def get_refresh_token_by_token(self, token: str) -> Optional[RefreshTokenDTO]:
        """Get refresh token by token string"""
        self._build_refresh_token_query()
        self._query_builder.where("token = %s AND expires_at > CURRENT_TIMESTAMP", token)

        result = await self._execute_query_single("Get refresh token by token")
        return self.map_to_refresh_token_dto(result) if result else None

    async def get_refresh_tokens_by_user_id(self, user_id: int) -> List[RefreshTokenDTO]:
        """Get all refresh tokens for user"""
        self._build_refresh_token_query()
        self._query_builder.where("user_id = %s AND expires_at > CURRENT_TIMESTAMP", user_id)
        self._query_builder.order_by("expires_at DESC")

        results = await self._execute_query_multiple("Get refresh tokens by user ID")
        return [self.map_to_refresh_token_dto(row) for row in results]

    async def create_refresh_token(self, token_data: CreateTokenDTO) -> RefreshTokenDTO:
        """Create refresh token"""
        query = f"""
            INSERT INTO {self.APP_NAME}_refresh_tokens (token, expires_at, user_id)
            VALUES (%s, %s, %s)
            RETURNING id, token, expires_at, user_id
        """

        params = [token_data.token, token_data.expires_at, token_data.user_id]

        try:
            result = await self._execute_custom_query_single(query, params, "Create refresh token")
        except Exception as e:
            if isinstance(e, (psycopg.Error, psycopg.DatabaseError, psycopg.IntegrityError)):
                raise TokenCreationError(f"Failed to create refresh token for user ID: {token_data.user_id}", e)
            raise TokenCreationError(f"Unexpected error creating refresh token for user ID: {token_data.user_id}", e)

        if not result:
            raise TokenCreationError(f"No result returned when creating refresh token for user: {token_data.user_id}")

        return self.map_to_refresh_token_dto(result)

    async def delete_refresh_token(self, token: str) -> bool:
        """Delete refresh token"""
        query = f"DELETE FROM {self.APP_NAME}_refresh_tokens WHERE token = %s"
        params = [token]

        try:
            result = await self._execute_custom_query_single(query, params, "Delete refresh token")
        except Exception as e:
            if isinstance(e, (psycopg.Error, psycopg.DatabaseError)):
                raise TokenDeletionError(f"Failed to delete refresh token: {token}", e)
            raise TokenDeletionError(f"Unexpected error deleting refresh token: {token}", e)

        return result is not None

    async def delete_expired_tokens(self) -> int:
        """Delete all expired tokens"""
        queries = [
            f"DELETE FROM {self.APP_NAME}_activation_tokens WHERE expires_at <= CURRENT_TIMESTAMP",
            f"DELETE FROM {self.APP_NAME}_password_reset_tokens WHERE expires_at <= CURRENT_TIMESTAMP",
            f"DELETE FROM {self.APP_NAME}_refresh_tokens WHERE expires_at <= CURRENT_TIMESTAMP"
        ]

        total_deleted = 0
        for query in queries:
            try:
                result = await self._execute_custom_query_single(query, [], "Delete expired tokens")
                if result:
                    total_deleted += 1
            except Exception as e:
                if isinstance(e, (psycopg.Error, psycopg.DatabaseError)):
                    raise TokenDeletionError("Failed to delete expired tokens", e)
                raise TokenDeletionError("Unexpected error deleting expired tokens", e)

        logger.info(f"Total expired token types deleted: {total_deleted}")
        return total_deleted

    async def delete_user_refresh_tokens(self, user_id: int) -> int:
        """Delete all refresh tokens for user"""
        query = f"DELETE FROM {self.APP_NAME}_refresh_tokens WHERE user_id = %s"
        params = [user_id]

        try:
            result = await self._execute_custom_query_single(query, params, "Delete user refresh tokens")
        except Exception as e:
            if isinstance(e, (psycopg.Error, psycopg.DatabaseError)):
                raise TokenDeletionError(f"Failed to delete refresh tokens for user ID: {user_id}", e)
            raise TokenDeletionError(f"Unexpected error deleting refresh tokens for user ID: {user_id}", e)

        return 1 if result is not None else 0

    def _build_activation_token_query(self) -> None:
        """Build base activation token query"""
        self._query_builder.reset().select("id", "token", "expires_at", "user_id")

    def _build_password_reset_token_query(self) -> None:
        """Build base password reset token query"""
        self._query_builder.reset().select("id", "token", "expires_at", "user_id")

    def _build_refresh_token_query(self) -> None:
        """Build base refresh token query"""
        self._query_builder.reset().select("id", "token", "expires_at", "user_id")
