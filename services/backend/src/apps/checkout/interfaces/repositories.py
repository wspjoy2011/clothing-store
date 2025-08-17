from abc import ABC, abstractmethod
from typing import Optional, List

from apps.checkout.dto import (
    CartTokenDTO,
    CartDTO,
    CartItemDTO,
    AddToCartRequestDTO,
    UpdateCartItemRequestDTO
)


class CartTokenRepositoryInterface(ABC):
    """Interface for cart token repository operations"""

    @abstractmethod
    async def create_cart_token(self, token: str) -> CartTokenDTO:
        """
        Create a new cart token for anonymous users

        Args:
            token: Unique token string

        Returns:
            Created CartTokenDTO
        """
        pass

    @abstractmethod
    async def get_cart_token_by_token(self, token: str) -> Optional[CartTokenDTO]:
        """
        Get cart token by token string

        Args:
            token: Token string to search for

        Returns:
            CartTokenDTO if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_cart_token_by_id(self, token_id: int) -> Optional[CartTokenDTO]:
        """
        Get cart token by ID

        Args:
            token_id: ID of the token to retrieve

        Returns:
            CartTokenDTO if found, None otherwise
        """
        pass

    @abstractmethod
    async def delete_expired_tokens(self) -> int:
        """
        Delete all expired tokens

        Returns:
            Number of deleted tokens
        """
        pass

    @abstractmethod
    async def is_token_valid(self, token: str) -> bool:
        """
        Check if token is valid and not expired

        Args:
            token: Token string to validate

        Returns:
            True if token is valid, False otherwise
        """
        pass


class CartRepositoryInterface(ABC):
    """Interface for cart repository operations"""

    @abstractmethod
    async def create_cart_for_user(self, user_id: int) -> CartDTO:
        """
        Create a new cart for authenticated user

        Args:
            user_id: ID of the user

        Returns:
            Created CartDTO
        """
        pass

    @abstractmethod
    async def create_cart_for_token(self, cart_token_id: int) -> CartDTO:
        """
        Create a new cart for anonymous user with token

        Args:
            cart_token_id: ID of the cart token

        Returns:
            Created CartDTO
        """
        pass

    @abstractmethod
    async def get_cart_by_user_id(self, user_id: int) -> Optional[CartDTO]:
        """
        Get cart by user ID

        Args:
            user_id: ID of the user

        Returns:
            CartDTO if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_cart_by_token_id(self, cart_token_id: int) -> Optional[CartDTO]:
        """
        Get cart by cart token ID

        Args:
            cart_token_id: ID of the cart token

        Returns:
            CartDTO if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_cart_by_id(self, cart_id: int) -> Optional[CartDTO]:
        """
        Get cart by cart ID

        Args:
            cart_id: ID of the cart

        Returns:
            CartDTO if found, None otherwise
        """
        pass

    @abstractmethod
    async def delete_cart(self, cart_id: int) -> bool:
        """
        Delete cart by ID

        Args:
            cart_id: ID of the cart to delete

        Returns:
            True if deleted successfully, False otherwise
        """
        pass

    @abstractmethod
    async def merge_carts(self, source_cart_id: int, target_cart_id: int) -> bool:
        """
        Merge items from source cart to target cart and delete source cart

        Args:
            source_cart_id: ID of the cart to merge from
            target_cart_id: ID of the cart to merge to

        Returns:
            True if merged successfully, False otherwise
        """
        pass


class CartItemRepositoryInterface(ABC):
    """Interface for cart item repository operations"""

    @abstractmethod
    async def add_item_to_cart(self, request_data: AddToCartRequestDTO, cart_id: int) -> CartItemDTO:
        """
        Add item to cart or update quantity if item already exists

        Args:
            request_data: Data for adding item to cart
            cart_id: ID of the cart

        Returns:
            Created or updated CartItemDTO
        """
        pass

    @abstractmethod
    async def get_cart_item_by_id(self, item_id: int) -> Optional[CartItemDTO]:
        """
        Get cart item by ID

        Args:
            item_id: ID of the cart item

        Returns:
            CartItemDTO if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_cart_items_by_cart_id(self, cart_id: int) -> List[CartItemDTO]:
        """
        Get all items in a cart

        Args:
            cart_id: ID of the cart

        Returns:
            List of CartItemDTO objects
        """
        pass

    @abstractmethod
    async def get_cart_item_by_cart_and_product(self, cart_id: int, product_id: int) -> Optional[CartItemDTO]:
        """
        Get cart item by cart ID and product ID

        Args:
            cart_id: ID of the cart
            product_id: ID of the product

        Returns:
            CartItemDTO if found, None otherwise
        """
        pass

    @abstractmethod
    async def update_cart_item(self, request_data: UpdateCartItemRequestDTO, cart_id: int) -> Optional[CartItemDTO]:
        """
        Update cart item quantity with cart ownership validation

        Args:
            request_data: Data for updating cart item (id, quantity)
            cart_id: ID of the cart to which the item must belong

        Returns:
            Updated CartItemDTO if successful, None otherwise
        """
        pass

    @abstractmethod
    async def remove_cart_item(self, item_id: int, cart_id: int) -> bool:
        """
        Remove item from cart with cart ownership validation

        Args:
            item_id: ID of the cart item to remove
            cart_id: ID of the cart (for ownership validation)

        Returns:
            True if removed successfully, False if item not found or doesn't belong to cart
        """
        pass

    @abstractmethod
    async def clear_cart_items(self, cart_id: int) -> bool:
        """
        Remove all items from cart

        Args:
            cart_id: ID of the cart to clear

        Returns:
            True if cleared successfully, False otherwise
        """
        pass

    @abstractmethod
    async def get_cart_items_count(self, cart_id: int) -> int:
        """
        Get total count of items in cart

        Args:
            cart_id: ID of the cart

        Returns:
            Number of items in the cart
        """
        pass

    @abstractmethod
    async def get_cart_total_quantity(self, cart_id: int) -> int:
        """
        Get total quantity of all items in cart

        Args:
            cart_id: ID of the cart

        Returns:
            Total quantity of all items
        """
        pass
