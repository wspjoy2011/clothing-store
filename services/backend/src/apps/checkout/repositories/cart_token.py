from typing import Optional
from datetime import datetime, timezone

from apps.checkout.dto import CartTokenDTO
from apps.checkout.interfaces.repositories import CartTokenRepositoryInterface
from db.interfaces import DAOInterface, SQLQueryBuilderInterface
from settings.logging_config import get_logger

logger = get_logger(__name__, "checkout")


class CartTokenRepository(CartTokenRepositoryInterface):
    """Repository implementation for cart token operations using SQL database"""

    APP_NAME = "checkout"

    def __init__(self, dao: DAOInterface, query_builder: SQLQueryBuilderInterface):
        """
        Initialize cart token repository

        Args:
            dao: Data Access Object for database operations
            query_builder: SQL query builder for constructing queries
        """
        self._dao = dao
        self._query_builder = query_builder

    async def create_cart_token(self, token: str) -> CartTokenDTO:
        """
        Create a new cart token for anonymous users

        Args:
            token: Unique token string

        Returns:
            Created CartTokenDTO
        """
        query = f"""
            INSERT INTO {self.APP_NAME}_cart_tokens (token)
            VALUES (%s)
            RETURNING id, token, expires_at, created_at, updated_at
        """

        result = await self._dao.execute(
            query=query,
            params=[token],
            fetch=True,
            fetch_one=True,
            model_class=CartTokenDTO
        )

        logger.info(f"Created cart token with ID: {result.id}")
        return result

    async def get_cart_token_by_token(self, token: str) -> Optional[CartTokenDTO]:
        """
        Get cart token by token string

        Args:
            token: Token string to search for

        Returns:
            CartTokenDTO if found, None otherwise
        """
        query = f"""
            SELECT id, token, expires_at, created_at, updated_at
            FROM {self.APP_NAME}_cart_tokens
            WHERE token = %s
        """

        result = await self._dao.execute(
            query=query,
            params=[token],
            fetch=True,
            fetch_one=True,
            model_class=CartTokenDTO
        )

        return result

    async def get_cart_token_by_id(self, token_id: int) -> Optional[CartTokenDTO]:
        """
        Get cart token by ID

        Args:
            token_id: ID of the token to retrieve

        Returns:
            CartTokenDTO if found, None otherwise
        """
        query = f"""
            SELECT id, token, expires_at, created_at, updated_at
            FROM {self.APP_NAME}_cart_tokens
            WHERE id = %s
        """

        result = await self._dao.execute(
            query=query,
            params=[token_id],
            fetch=True,
            fetch_one=True,
            model_class=CartTokenDTO
        )

        return result

    async def delete_expired_tokens(self) -> int:
        """
        Delete all expired tokens

        Returns:
            Number of deleted tokens
        """
        count_query = f"""
            SELECT COUNT(*) as count
            FROM {self.APP_NAME}_cart_tokens
            WHERE expires_at < %s
        """

        current_time = datetime.now(timezone.utc)
        count_result = await self._dao.execute(
            query=count_query,
            params=[current_time],
            fetch=True,
            fetch_one=True,
            as_dict=True
        )

        deleted_count = count_result['count'] if count_result else 0

        delete_query = f"""
            DELETE FROM {self.APP_NAME}_cart_tokens
            WHERE expires_at < %s
        """

        await self._dao.execute(
            query=delete_query,
            params=[current_time],
            fetch=False
        )

        logger.info(f"Deleted {deleted_count} expired cart tokens")
        return deleted_count

    async def is_token_valid(self, token: str) -> bool:
        """
        Check if token is valid and not expired

        Args:
            token: Token string to validate

        Returns:
            True if token is valid, False otherwise
        """
        query = f"""
            SELECT COUNT(*) as count
            FROM {self.APP_NAME}_cart_tokens
            WHERE token = %s AND expires_at > %s
        """

        current_time = datetime.now(timezone.utc)
        result = await self._dao.execute(
            query=query,
            params=[token, current_time],
            fetch=True,
            fetch_one=True,
            as_dict=True
        )

        return result['count'] > 0 if result else False
