"""Test doubles for the cart service."""

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, List, Optional

from apps.checkout.dto.cart import CartItemDTO


@dataclass
class FakeInventory:
    """Inventory attached to a product"""

    base_price: Decimal = Decimal("10.00")
    sale_price: Optional[Decimal] = None
    is_in_stock: bool = True


@dataclass
class FakeProduct:
    """Product returned by the catalog"""

    product_id: int
    product_display_name: str = "Test Product"
    slug: str = "test-product"
    image_url: str = "http://example.com/image.jpg"
    inventory: FakeInventory = None

    def __post_init__(self):
        if self.inventory is None:
            self.inventory = FakeInventory()


class FakeCatalogService:
    """Catalog reporting a configurable amount of available stock"""

    def __init__(self, available_quantity: int = 100):
        self.available_quantity = available_quantity
        self.availability_checks: List[tuple] = []

    async def get_product_by_id(self, product_id: int) -> Optional[FakeProduct]:
        """Return a product for any identifier"""
        return FakeProduct(product_id=product_id)

    async def check_product_availability(self, product_id: int, quantity: int) -> bool:
        """Record the check and answer from the configured stock"""
        self.availability_checks.append((product_id, quantity))
        return quantity <= self.available_quantity


@dataclass
class FakeCart:
    """Cart owned by a user or a token"""

    id: int = 1
    user_id: Optional[int] = 1
    cart_token_id: Optional[int] = None
    created_at: datetime = datetime(2026, 1, 1, tzinfo=timezone.utc)
    updated_at: datetime = datetime(2026, 1, 1, tzinfo=timezone.utc)


class FakeCartRepository:
    """Cart repository returning one cart"""

    def __init__(self, cart: Optional[FakeCart] = None):
        self.cart = cart if cart is not None else FakeCart()

    async def get_cart_by_user_id(self, user_id: int) -> FakeCart:
        """Return the single cart"""
        return self.cart

    async def create_cart_for_user(self, user_id: int) -> FakeCart:
        """Return the single cart"""
        return self.cart


class FakeCartItemRepository:
    """Cart item repository backed by one stored item

    The update mirrors the real statement, which re-checks stock inside the
    UPDATE, so a test can reproduce stock being taken between check and write.
    """

    def __init__(self, item: Optional[CartItemDTO] = None, available_quantity: int = 10 ** 6):
        self.item = item
        self.available_quantity = available_quantity
        self.updates: List[Any] = []

    async def get_cart_item_by_id(self, item_id: int) -> Optional[CartItemDTO]:
        """Return the stored item when the identifier matches"""
        if self.item is not None and self.item.id == item_id:
            return self.item
        return None

    async def get_cart_items_by_cart_id(self, cart_id: int) -> List[CartItemDTO]:
        """Return the stored item when it belongs to the cart"""
        if self.item is not None and self.item.cart_id == cart_id:
            return [self.item]
        return []

    async def get_cart_items_count(self, cart_id: int) -> int:
        """Count the stored items of the cart"""
        return len(await self.get_cart_items_by_cart_id(cart_id))

    async def get_cart_total_quantity(self, cart_id: int) -> int:
        """Sum the quantities stored in the cart"""
        return sum(item.quantity for item in await self.get_cart_items_by_cart_id(cart_id))

    async def update_cart_item(self, request_data: Any, cart_id: int) -> Optional[CartItemDTO]:
        """Record the update and return the item, mirroring the stock guard in SQL"""
        self.updates.append((request_data.cart_item_id, request_data.quantity, cart_id))

        if self.item is None or self.item.cart_id != cart_id:
            return None

        if request_data.quantity > self.available_quantity:
            return None

        self.item = CartItemDTO(
            id=self.item.id,
            cart_id=self.item.cart_id,
            product_id=self.item.product_id,
            quantity=request_data.quantity,
            added_at=self.item.added_at,
            updated_at=datetime(2026, 1, 2, tzinfo=timezone.utc)
        )
        return self.item


class FakeCartTokenRepository:
    """Cart token repository that is never reached in these tests"""

    async def get_cart_token_by_token(self, token: str) -> None:
        """Report the token as unknown"""
        return None


def build_cart_item(item_id: int = 1, cart_id: int = 1, product_id: int = 10, quantity: int = 1) -> CartItemDTO:
    """
    Build a stored cart item

    Args:
        item_id: Identifier of the item
        cart_id: Cart the item belongs to
        product_id: Product the item refers to
        quantity: Quantity currently stored

    Returns:
        Cart item ready to be served by the repository double
    """
    return CartItemDTO(
        id=item_id,
        cart_id=cart_id,
        product_id=product_id,
        quantity=quantity,
        added_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        updated_at=datetime(2026, 1, 1, tzinfo=timezone.utc)
    )
