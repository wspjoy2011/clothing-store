import secrets
from datetime import datetime, timezone
from typing import Optional
from decimal import Decimal

from apps.checkout.dto import (
    CartTokenResponseDTO,
    CartResponseDTO,
    CartItemResponseDTO,
    CartSummaryDTO,
    AddToCartRequestDTO,
    UpdateCartItemRequestDTO,
)
from apps.checkout.interfaces.repositories import (
    CartTokenRepositoryInterface,
    CartRepositoryInterface,
    CartItemRepositoryInterface
)
from apps.checkout.interfaces import CartServiceInterface
from apps.checkout.exceptions import (
    CartTokenCreationError,
    CartNotFoundError, ProductNotFoundError, InsufficientStockError,
)
from apps.catalog.interfaces.services import CatalogServiceInterface
from settings.logging_config import get_logger

logger = get_logger(__name__, "checkout")


class CartService(CartServiceInterface):
    """Service for cart operations with business logic"""

    def __init__(
            self,
            cart_token_repository: CartTokenRepositoryInterface,
            cart_repository: CartRepositoryInterface,
            cart_item_repository: CartItemRepositoryInterface,
            catalog_service: CatalogServiceInterface
    ):
        """
        Initialize cart service

        Args:
            cart_token_repository: Repository for cart token operations
            cart_repository: Repository for cart operations
            cart_item_repository: Repository for cart item operations
            catalog_service: Service for product information
        """
        self._cart_token_repository = cart_token_repository
        self._cart_repository = cart_repository
        self._cart_item_repository = cart_item_repository
        self._catalog_service = catalog_service

    async def create_cart_token(self) -> CartTokenResponseDTO:
        """
        Create a new cart token for anonymous users

        Business logic: Generate unique token, create token record, return token with expiration

        Returns:
            Cart token response with token and expiration date

        Raises:
            CartTokenCreationError: If token creation fails
        """
        logger.info("Creating new cart token for anonymous user")

        token = secrets.token_urlsafe(32)

        try:
            cart_token = await self._cart_token_repository.create_cart_token(token)
        except Exception as e:
            logger.error(f"Failed to create cart token: {e}")
            raise CartTokenCreationError(f"Failed to create cart token: {e}", e)
        else:
            logger.info(f"Cart token created successfully: {token[:10]}...")

            return CartTokenResponseDTO(
                token=cart_token.token,
                expires_at=cart_token.expires_at
            )

    async def get_or_create_cart_for_user(self, user_id: int) -> CartResponseDTO:
        """
        Get existing cart for user or create new one if doesn't exist

        Business logic: Check if user has cart, create if not exists, load cart items with product details

        Args:
            user_id: ID of the authenticated user

        Returns:
            Complete cart information with items and totals

        Raises:
            CartValidationError: If cart operations fail
        """
        logger.info(f"Getting or creating cart for user: {user_id}")

        cart = await self._cart_repository.get_cart_by_user_id(user_id)

        if not cart:
            cart = await self._cart_repository.create_cart_for_user(user_id)
            logger.info(f"New cart created for user {user_id}: cart_id={cart.id}")

        return await self._build_cart_response(cart)

    async def get_or_create_cart_for_token(self, token: str) -> CartResponseDTO:
        """
        Get existing cart for token or create new one if doesn't exist

        Business logic: Validate token, check if cart exists, create if not, load items with product details

        Args:
            token: Cart token string

        Returns:
            Complete cart information with items and totals

        Raises:
            CartNotFoundError: If token is invalid or expired
            CartValidationError: If cart operations fail
        """
        logger.info(f"Getting or creating cart for token: {token[:10]}...")

        cart_token = await self._cart_token_repository.get_cart_token_by_token(token)
        if not cart_token:
            logger.warning(f"Cart token not found: {token[:10]}...")
            raise CartNotFoundError(f"Cart token not found: {token[:10]}...")

        if cart_token.expires_at <= datetime.now(timezone.utc):
            logger.warning(f"Cart token expired: {token[:10]}...")
            raise CartNotFoundError(f"Cart token expired: {token[:10]}...")

        cart = await self._cart_repository.get_cart_by_token_id(cart_token.id)

        if not cart:
            cart = await self._cart_repository.create_cart_for_token(cart_token.id)
            logger.info(f"New cart created for token {token[:10]}...: cart_id={cart.id}")

        return await self._build_cart_response(cart)

    async def add_item_to_cart(
            self,
            request_data: AddToCartRequestDTO,
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

        Raises:
            CartNotFoundError: If cart cannot be found or created
            ProductNotFoundError: If product does not exist
            InsufficientStockError: If not enough stock available
        """
        logger.info(f"Adding item to cart: product_id={request_data.product_id}, quantity={request_data.quantity}")

        if user_id:
            cart_response = await self.get_or_create_cart_for_user(user_id)
        elif token:
            cart_response = await self.get_or_create_cart_for_token(token)
        else:
            raise CartNotFoundError("Either user_id or token must be provided")

        product = await self._catalog_service.get_product_by_id(request_data.product_id)
        if not product:
            logger.warning(f"Product not found: {request_data.product_id}")
            raise ProductNotFoundError(f"Product with ID {request_data.product_id} not found")

        is_available = await self._catalog_service.check_product_availability(
            request_data.product_id,
            request_data.quantity
        )
        if not is_available:
            logger.warning(f"Insufficient stock for product {request_data.product_id}, requested: {request_data.quantity}")
            raise InsufficientStockError(f"Insufficient stock for product {request_data.product_id}")

        cart_item = await self._cart_item_repository.add_item_to_cart(request_data, cart_response.id)

        logger.info(f"Item added to cart successfully: cart_id={cart_response.id}, item_id={cart_item.id}")

        return self._build_cart_item_response(cart_item, product)

    async def update_cart_item(
            self,
            request_data: UpdateCartItemRequestDTO,
            user_id: Optional[int] = None,
            token: Optional[str] = None
    ) -> CartItemResponseDTO:
        """Not implemented yet"""
        raise NotImplementedError("update_cart_item method is not implemented yet")

    async def remove_cart_item(
            self,
            item_id: int,
            user_id: Optional[int] = None,
            token: Optional[str] = None
    ) -> bool:
        """Not implemented yet"""
        raise NotImplementedError("remove_cart_item method is not implemented yet")

    async def clear_cart(
            self,
            user_id: Optional[int] = None,
            token: Optional[str] = None
    ) -> bool:
        """Not implemented yet"""
        raise NotImplementedError("clear_cart method is not implemented yet")

    async def get_cart_summary(
            self,
            user_id: Optional[int] = None,
            token: Optional[str] = None
    ) -> Optional[CartSummaryDTO]:
        """Not implemented yet"""
        raise NotImplementedError("get_cart_summary method is not implemented yet")

    async def merge_anonymous_cart(self, user_id: int, token: str) -> CartResponseDTO:
        """Not implemented yet"""
        raise NotImplementedError("merge_anonymous_cart method is not implemented yet")

    async def validate_cart_items_availability(
            self,
            user_id: Optional[int] = None,
            token: Optional[str] = None
    ) -> CartResponseDTO:
        """Not implemented yet"""
        raise NotImplementedError("validate_cart_items_availability method is not implemented yet")

    async def _build_cart_response(self, cart) -> CartResponseDTO:
        """Build complete cart response with items and product details"""
        cart_items = await self._cart_item_repository.get_cart_items_by_cart_id(cart.id)

        items_response = []
        total_amount = Decimal('0.00')
        total_discount = Decimal('0.00')
        total_items = 0

        for item in cart_items:
            product = await self._catalog_service.get_product_by_id(item.product_id)
            item_response = self._build_cart_item_response(item, product)
            items_response.append(item_response)

            total_amount += item_response.total_price
            total_items += item.quantity

            if item_response.sale_price and item_response.sale_price < item_response.unit_price:
                item_discount = (item_response.unit_price - item_response.sale_price) * item.quantity
                total_discount += item_discount

        final_amount = total_amount - total_discount

        return CartResponseDTO(
            id=cart.id,
            items=items_response,
            total_items=total_items,
            total_amount=total_amount,
            total_discount=total_discount,
            final_amount=final_amount,
            created_at=cart.created_at,
            updated_at=cart.updated_at
        )

    @staticmethod
    def _build_cart_item_response(cart_item, product) -> CartItemResponseDTO:
        """Build cart item response with product details"""
        is_available = bool(product and product.inventory and product.inventory.is_in_stock)

        unit_price = product.inventory.base_price if product and product.inventory else Decimal('0.00')
        sale_price = None
        if product and product.inventory and product.inventory.sale_price:
            sale_price = product.inventory.sale_price

        return CartItemResponseDTO(
            id=cart_item.id,
            product_id=cart_item.product_id,
            product_name=product.product_display_name if product else "Unknown Product",
            product_slug=product.slug if product else "unknown",
            product_image_url=product.image_url if product else "",
            quantity=cart_item.quantity,
            unit_price=unit_price,
            sale_price=sale_price,
            total_price=unit_price * cart_item.quantity,
            is_available=is_available,
            added_at=cart_item.added_at
        )
