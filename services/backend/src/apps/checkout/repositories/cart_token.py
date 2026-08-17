from typing import Optional

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


