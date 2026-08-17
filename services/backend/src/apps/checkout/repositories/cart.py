from typing import Optional

import psycopg

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

    async def get_cart_by_id(self, cart_id: int) -> Optional[CartDTO]:
        """
        Get cart by cart ID

        Args:
            cart_id: ID of the cart

        Returns:
            CartDTO if found, None otherwise
        """
        query = f"""
            SELECT id, user_id, cart_token_id, created_at, updated_at
            FROM {self.APP_NAME}_cart
            WHERE id = %s
        """

        result = await self._dao.execute(
            query=query,
            params=[cart_id],
            fetch=True,
            fetch_one=True,
            model_class=CartDTO
        )

        return result

    async def delete_cart(self, cart_id: int) -> bool:
        """
        Delete cart by ID

        Args:
            cart_id: ID of the cart to delete

        Returns:
            True if deleted successfully, False otherwise
        """
        query = f"DELETE FROM {self.APP_NAME}_cart WHERE id = %s"

        try:
            await self._dao.execute(
                query=query,
                params=[cart_id],
                fetch=False
            )
        except psycopg.Error as e:
            logger.error(f"Database error deleting cart {cart_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to delete cart {cart_id}: {e}")
            return False

        logger.info(f"Deleted cart with ID: {cart_id}")
        return True

    async def merge_carts(self, source_cart_id: int, target_cart_id: int) -> bool:
        """
        Merge items from source cart to target cart and delete source cart

        Args:
            source_cart_id: ID of the cart to merge from
            target_cart_id: ID of the cart to merge to

        Returns:
            True if merged successfully, False otherwise
        """
        merge_query = f"""
            INSERT INTO {self.APP_NAME}_cart_items (cart_id, product_id, quantity)
            SELECT %s, sci.product_id, sci.quantity
            FROM {self.APP_NAME}_cart_items sci
            WHERE sci.cart_id = %s
            ON CONFLICT (cart_id, product_id)
            DO UPDATE SET 
                quantity = {self.APP_NAME}_cart_items.quantity + EXCLUDED.quantity,
                updated_at = CURRENT_TIMESTAMP
        """

        try:
            await self._dao.execute(
                query=merge_query,
                params=[target_cart_id, source_cart_id],
                fetch=False
            )
        except psycopg.Error as e:
            logger.error(f"Database error merging carts {source_cart_id} -> {target_cart_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to merge carts {source_cart_id} -> {target_cart_id}: {e}")
            return False

        delete_query = f"DELETE FROM {self.APP_NAME}_cart WHERE id = %s"
        try:
            await self._dao.execute(
                query=delete_query,
                params=[source_cart_id],
                fetch=False
            )
        except psycopg.Error as e:
            logger.error(f"Database error deleting source cart {source_cart_id}: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to delete source cart {source_cart_id}: {e}")
            return False

        logger.info(f"Merged cart {source_cart_id} into cart {target_cart_id}")
        return True
