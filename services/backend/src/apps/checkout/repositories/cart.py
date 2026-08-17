from typing import Optional

from apps.checkout.dto import CartDTO
from apps.checkout.interfaces.repositories import CartRepositoryInterface
from db.interfaces import DAOInterface, SQLQueryBuilderInterface
from settings.logging_config import get_logger

logger = get_logger(__name__, "checkout")


class CartRepository(CartRepositoryInterface):
    """Repository implementation for cart operations using SQL database"""

    APP_NAME = "checkout"

    def __init__(self, dao: DAOInterface, query_builder: SQLQueryBuilderInterface):
        """
        Initialize cart repository

        Args:
            dao: Data Access Object for database operations
            query_builder: SQL query builder for constructing queries
        """
        self._dao = dao
        self._query_builder = query_builder

    async def create_cart_for_user(self, user_id: int) -> CartDTO:
        """
        Create a new cart for authenticated user

        Args:
            user_id: ID of the user

        Returns:
            Created CartDTO
        """
        query = f"""
            INSERT INTO {self.APP_NAME}_cart (user_id)
            VALUES (%s)
            ON CONFLICT (user_id) DO UPDATE SET updated_at = checkout_cart.updated_at
            RETURNING id, user_id, cart_token_id, created_at, updated_at
        """

        result = await self._dao.execute(
            query=query,
            params=[user_id],
            fetch=True,
            fetch_one=True,
            model_class=CartDTO
        )

        logger.info(f"Created cart for user {user_id} with ID: {result.id}")
        return result

    async def create_cart_for_token(self, cart_token_id: int) -> CartDTO:
        """
        Create a new cart for anonymous user with token

        Args:
            cart_token_id: ID of the cart token

        Returns:
            Created CartDTO
        """
        query = f"""
            INSERT INTO {self.APP_NAME}_cart (cart_token_id)
            VALUES (%s)
            ON CONFLICT (cart_token_id) DO UPDATE SET updated_at = checkout_cart.updated_at
            RETURNING id, user_id, cart_token_id, created_at, updated_at
        """

        result = await self._dao.execute(
            query=query,
            params=[cart_token_id],
            fetch=True,
            fetch_one=True,
            model_class=CartDTO
        )

        logger.info(f"Created cart for token {cart_token_id} with ID: {result.id}")
        return result

    async def get_cart_by_user_id(self, user_id: int) -> Optional[CartDTO]:
        """
        Get cart by user ID

        Args:
            user_id: ID of the user

        Returns:
            CartDTO if found, None otherwise
        """
        query = f"""
            SELECT id, user_id, cart_token_id, created_at, updated_at
            FROM {self.APP_NAME}_cart
            WHERE user_id = %s
        """

        result = await self._dao.execute(
            query=query,
            params=[user_id],
            fetch=True,
            fetch_one=True,
            model_class=CartDTO
        )

        return result

    async def get_cart_by_token_id(self, cart_token_id: int) -> Optional[CartDTO]:
        """
        Get cart by cart token ID

        Args:
            cart_token_id: ID of the cart token

        Returns:
            CartDTO if found, None otherwise
        """
        query = f"""
            SELECT id, user_id, cart_token_id, created_at, updated_at
            FROM {self.APP_NAME}_cart
            WHERE cart_token_id = %s
        """

        result = await self._dao.execute(
            query=query,
            params=[cart_token_id],
            fetch=True,
            fetch_one=True,
            model_class=CartDTO
        )

        return result



