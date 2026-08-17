from typing import List, Optional

import psycopg

from apps.checkout.dto import AddToCartRequestDTO, CartItemDTO, UpdateCartItemRequestDTO
from apps.checkout.exceptions.repositories import CartStorageError
from apps.checkout.interfaces.repositories import CartItemRepositoryInterface
from db.interfaces import DAOInterface, SQLQueryBuilderInterface
from settings.logging_config import get_logger

logger = get_logger(__name__, "checkout")


class CartItemRepository(CartItemRepositoryInterface):
    """Repository implementation for cart item operations using SQL database"""

    APP_NAME = "checkout"

    def __init__(self, dao: DAOInterface, query_builder: SQLQueryBuilderInterface):
        """
        Initialize cart item repository

        Args:
            dao: Data Access Object for database operations
            query_builder: SQL query builder for constructing queries
        """
        self._dao = dao
        self._query_builder = query_builder

    async def add_item_to_cart(self, request_data: AddToCartRequestDTO, cart_id: int) -> Optional[CartItemDTO]:
        """
        Add item to cart or update quantity if item already exists

        On conflict the quantities are summed, so the caller must validate the
        resulting total rather than the increment, while holding the inventory row.

        Args:
            request_data: Data for adding item to cart
            cart_id: ID of the cart

        Returns:
            Created or updated CartItemDTO
        """
        query = f"""
            INSERT INTO {self.APP_NAME}_cart_items (cart_id, product_id, quantity)
            VALUES (%s, %s, %s)
            ON CONFLICT (cart_id, product_id)
            DO UPDATE SET
                quantity = {self.APP_NAME}_cart_items.quantity + EXCLUDED.quantity,
                updated_at = CURRENT_TIMESTAMP
            RETURNING id, cart_id, product_id, quantity, added_at, updated_at
        """

        result = await self._dao.execute(
            query=query,
            params=[cart_id, request_data.product_id, request_data.quantity],
            fetch=True,
            fetch_one=True,
            model_class=CartItemDTO
        )

        logger.info(
            f"Added/updated item in cart {cart_id}: product {request_data.product_id}, "
            f"quantity {request_data.quantity}"
        )
        return result

    async def get_cart_item_by_id(self, item_id: int) -> Optional[CartItemDTO]:
        """
        Get cart item by ID

        Args:
            item_id: ID of the cart item

        Returns:
            CartItemDTO if found, None otherwise
        """
        query = f"""
            SELECT id, cart_id, product_id, quantity, added_at, updated_at
            FROM {self.APP_NAME}_cart_items
            WHERE id = %s
        """

        result = await self._dao.execute(
            query=query,
            params=[item_id],
            fetch=True,
            fetch_one=True,
            model_class=CartItemDTO
        )

        return result

    async def get_cart_items_by_cart_id(self, cart_id: int) -> List[CartItemDTO]:
        """
        Get all items in a cart

        Args:
            cart_id: ID of the cart

        Returns:
            List of CartItemDTO objects
        """
        query = f"""
            SELECT id, cart_id, product_id, quantity, added_at, updated_at
            FROM {self.APP_NAME}_cart_items
            WHERE cart_id = %s
            ORDER BY added_at
        """

        results = await self._dao.execute(
            query=query,
            params=[cart_id],
            fetch=True,
            fetch_one=False,
            model_class=CartItemDTO
        )

        return results or []

    async def get_cart_item_by_cart_and_product(self, cart_id: int, product_id: int) -> Optional[CartItemDTO]:
        """
        Get cart item by cart ID and product ID

        Args:
            cart_id: ID of the cart
            product_id: ID of the product

        Returns:
            CartItemDTO if found, None otherwise
        """
        query = f"""
            SELECT id, cart_id, product_id, quantity, added_at, updated_at
            FROM {self.APP_NAME}_cart_items
            WHERE cart_id = %s AND product_id = %s
        """

        result = await self._dao.execute(
            query=query,
            params=[cart_id, product_id],
            fetch=True,
            fetch_one=True,
            model_class=CartItemDTO
        )

        return result

    async def update_cart_item(self, request_data: UpdateCartItemRequestDTO, cart_id: int) -> Optional[CartItemDTO]:
        """
        Update cart item quantity with cart ownership and stock validation

        Stock is validated by the caller while it holds the inventory row, so this
        statement only enforces ownership.

        Args:
            request_data: Data for updating cart item
            cart_id: ID of the cart to which the item must belong

        Returns:
            Updated CartItemDTO, or None when the item is absent or owned by
            another cart
        """
        query = f"""
            UPDATE {self.APP_NAME}_cart_items
            SET quantity = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s AND cart_id = %s
            RETURNING id, cart_id, product_id, quantity, added_at, updated_at
        """

        result = await self._dao.execute(
            query=query,
            params=[request_data.quantity, request_data.cart_item_id, cart_id],
            fetch=True,
            fetch_one=True,
            model_class=CartItemDTO
        )

        if result:
            logger.info(
                f"Updated cart item {request_data.cart_item_id} quantity to {request_data.quantity} in cart {cart_id}"
            )
        else:
            logger.warning(
                f"Cart item {request_data.cart_item_id} not updated in cart {cart_id}: "
                f"it is missing or belongs to another cart"
            )

        return result

    async def remove_cart_item(self, item_id: int, cart_id: int) -> bool:
        """
        Remove item from cart with cart ownership validation

        Args:
            item_id: ID of the cart item to remove
            cart_id: ID of the cart (for ownership validation)

        Returns:
            True if removed, False if no such item belongs to that cart

        Raises:
            CartStorageError: If the statement could not be carried out, which is
                not the same answer as "no such item"
        """
        query = f"""
            DELETE FROM {self.APP_NAME}_cart_items
            WHERE id = %s AND cart_id = %s
            RETURNING id
        """

        try:
            result = await self._dao.execute(
                query=query,
                params=[item_id, cart_id],
                fetch=True,
                fetch_one=True,
                as_dict=True
            )
        except psycopg.Error as e:
            logger.error(f"Database error removing cart item {item_id} from cart {cart_id}: {e}")
            raise CartStorageError(f"Cart item {item_id} could not be removed from cart {cart_id}", e)
        except Exception as e:
            logger.error(f"Failed to remove cart item {item_id} from cart {cart_id}: {e}")
            raise CartStorageError(f"Cart item {item_id} could not be removed from cart {cart_id}", e)
        else:
            if result:
                logger.info(f"Removed cart item {item_id} from cart {cart_id}")
                return True
            else:
                logger.warning(f"Cart item {item_id} not found in cart {cart_id} or doesn't belong to this cart")
                return False



