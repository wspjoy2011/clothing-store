from abc import ABC, abstractmethod
from typing import Optional

from apps.checkout.dto import (
    CartTokenResponseDTO,
    CartResponseDTO,
    CartItemResponseDTO,
    CartSummaryDTO,
    AddToCartRequestDTO,
    UpdateCartItemRequestDTO,
)


class CartServiceInterface(ABC):
    """Interface for cart service operations"""

    @abstractmethod
    async def create_cart_token(self) -> CartTokenResponseDTO:
        """
        Create a new cart token for anonymous users

        Business logic: Generate unique token, create token record, return token with expiration

        Returns:
            Cart token response with token and expiration date
        """
        pass

    @abstractmethod
    async def get_or_create_cart_for_user(self, user_id: int) -> CartResponseDTO:
        """
        Get existing cart for user or create new one if doesn't exist

        Business logic: Check if user has cart, create if not exists, load cart items with product details

        Args:
            user_id: ID of the authenticated user

        Returns:
            Complete cart information with items and totals
        """
        pass

    @abstractmethod
    async def get_or_create_cart_for_token(self, token: str) -> CartResponseDTO:
        """
        Get existing cart for token or create new one if doesn't exist

        Business logic: Validate token, check if cart exists, create if not, load items with product details

        Args:
            token: Cart token string

        Returns:
            Complete cart information with items and totals
        """
        pass

    @abstractmethod
    async def add_item_to_cart(
            self, request_data: AddToCartRequestDTO,
            user_id: Optional[int] = None,
            token: Optional[str] = None
    ) -> CartItemResponseDTO:
        """
        Add item to cart with business validation

        Business logic: Validate product exists, check stock availability, get/create cart,
        add item or update quantity, return item with product details and pricing

        Args:
            request_data: Data for adding item to cart
            user_id: ID of authenticated user (mutually exclusive with token)
            token: Cart token for anonymous user (mutually exclusive with user_id)

        Returns:
            Added cart item with complete product information
        """
        pass

    @abstractmethod
    async def update_cart_item(
            self,
            request_data: UpdateCartItemRequestDTO,
            user_id: Optional[int] = None,
            token: Optional[str] = None
    ) -> CartItemResponseDTO:
        """
        Update cart item quantity with validation

        Business logic: Validate ownership, check stock availability, update quantity,
        return updated item with product details

        Args:
            request_data: Data for updating cart item
            user_id: ID of authenticated user (mutually exclusive with token)
            token: Cart token for anonymous user (mutually exclusive with user_id)

        Returns:
            Updated cart item with complete information
        """
        pass

    @abstractmethod
    async def remove_cart_item(
            self,
            item_id: int,
            user_id: Optional[int] = None,
            token: Optional[str] = None
    ) -> bool:
        """
        Remove item from cart with ownership validation

        Business logic: Validate ownership, remove item, return success status

        Args:
            item_id: ID of the cart item to remove
            user_id: ID of authenticated user (mutually exclusive with token)
            token: Cart token for anonymous user (mutually exclusive with user_id)

        Returns:
            True if removed successfully
        """
        pass




    @abstractmethod
    async def validate_cart_items_availability(
            self, user_id: Optional[int] = None,
            token: Optional[str] = None
    ) -> CartResponseDTO:
        """
        Validate all cart items are still available and update availability status

        Business logic: Check each item's stock, update availability flags,
        return cart with updated availability information

        Args:
            user_id: ID of authenticated user (mutually exclusive with token)
            token: Cart token for anonymous user (mutually exclusive with user_id)

        Returns:
            Cart with updated item availability information
        """
        pass
