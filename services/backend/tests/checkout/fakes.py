"""Test doubles for the cart service."""

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, List, Optional

from apps.checkout.dto.cart import CartItemDTO
from apps.checkout.dto.tokens import CartTokenDTO
from apps.checkout.interfaces.repositories import (
    CartItemRepositoryInterface,
    CartRepositoryInterface,
    CartTokenRepositoryInterface
)


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
    product_display_name: Optional[str] = "Test Product"
    slug: Optional[str] = "test-product"
    image_url: Optional[str] = "http://example.com/image.jpg"
    inventory: FakeInventory = None

    def __post_init__(self):
        if self.inventory is None:
            self.inventory = FakeInventory()


class FakeCatalogService:
    """Catalog reporting a configurable amount of available stock"""

    def __init__(
            self,
            available_quantity: int = 100,
            product: Optional[FakeProduct] = None,
            sellable: bool = True,
            journal: Optional[List[str]] = None
    ):
        self.available_quantity = available_quantity
        self.sellable = sellable
        self.product = product
        self.journal = journal if journal is not None else []
        self.holds: List[int] = []
        self.holds_inside_transaction: List[bool] = []

    async def get_product_by_id(self, product_id: int) -> Optional[FakeProduct]:
        """Return the configured product, or a complete one by default"""
        if self.product is not None:
            return self.product
        return FakeProduct(product_id=product_id)

    async def hold_available_quantity(self, product_id: int) -> Optional[int]:
        """Record the hold, whether a transaction was open, and report the stock"""
        from db.transaction import get_current_transaction

        self.journal.append("hold")
        self.holds.append(product_id)
        self.holds_inside_transaction.append(get_current_transaction() is not None)
        return self.available_quantity if self.sellable else None


@dataclass
class FakeCart:
    """Cart owned by a user or a token"""

    id: int = 1
    user_id: Optional[int] = 1
    cart_token_id: Optional[int] = None
    created_at: datetime = datetime(2026, 1, 1, tzinfo=timezone.utc)
    updated_at: datetime = datetime(2026, 1, 1, tzinfo=timezone.utc)


class FakeCartRepository(CartRepositoryInterface):
    """Cart repository returning one cart

    Implementing the interface is the point: a method added to the contract has to
    be answered here too, instead of leaving every test passing against a double
    that silently lacks it.
    """

    def __init__(self, cart: Optional[FakeCart] = None):
        self.cart = cart if cart is not None else FakeCart()

    async def get_cart_by_user_id(self, user_id: int) -> FakeCart:
        """Return the single cart"""
        return self.cart

    async def get_cart_by_token_id(self, cart_token_id: int) -> FakeCart:
        """Return the single cart"""
        return self.cart

    async def create_cart_for_user(self, user_id: int) -> FakeCart:
        """Return the single cart"""
        return self.cart

    async def create_cart_for_token(self, cart_token_id: int) -> FakeCart:
        """Return the single cart"""
        return self.cart


class FakeCartItemRepository(CartItemRepositoryInterface):
    """Cart item repository backed by one stored item

    Like the real statement, the update enforces ownership only: stock is decided
    by the caller while it holds the inventory row.
    """

    def __init__(self, item: Optional[CartItemDTO] = None, journal: Optional[List[str]] = None):
        self.item = item
        self.journal = journal if journal is not None else []
        self.additions: List[Any] = []
        self.updates: List[Any] = []
        self.removals: List[Any] = []

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

    async def get_cart_item_by_cart_and_product(self, cart_id: int, product_id: int) -> Optional[CartItemDTO]:
        """Return the stored item when it matches the cart and product"""
        self.journal.append("read")
        if self.item is not None and self.item.cart_id == cart_id and self.item.product_id == product_id:
            return self.item
        return None

    async def add_item_to_cart(self, request_data: Any, cart_id: int) -> CartItemDTO:
        """Store the item, summing the quantity when it is already there"""
        self.additions.append((request_data.product_id, request_data.quantity, cart_id))
        existing = await self.get_cart_item_by_cart_and_product(cart_id, request_data.product_id)
        quantity = request_data.quantity + (existing.quantity if existing else 0)

        self.item = CartItemDTO(
            id=existing.id if existing else 1,
            cart_id=cart_id,
            product_id=request_data.product_id,
            quantity=quantity,
            added_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            updated_at=datetime(2026, 1, 2, tzinfo=timezone.utc)
        )
        return self.item

    async def remove_cart_item(self, item_id: int, cart_id: int) -> bool:
        """Forget the stored item when it belongs to that cart"""
        self.removals.append((item_id, cart_id))

        if self.item is None or self.item.id != item_id or self.item.cart_id != cart_id:
            return False

        self.item = None
        return True

    async def update_cart_item(self, request_data: Any, cart_id: int) -> Optional[CartItemDTO]:
        """Record the update and return the item, enforcing ownership only"""
        self.updates.append((request_data.cart_item_id, request_data.quantity, cart_id))

        if self.item is None or self.item.cart_id != cart_id:
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


class FakeCartTokenRepository(CartTokenRepositoryInterface):
    """Cart token repository holding at most one issued token"""

    def __init__(self, token: Optional[CartTokenDTO] = None):
        self.token = token
        self.created: List[str] = []

    async def create_cart_token(self, token: str) -> CartTokenDTO:
        """Store the issued token"""
        self.created.append(token)
        self.token = CartTokenDTO(
            id=1,
            token=token,
            expires_at=datetime(2027, 1, 1, tzinfo=timezone.utc),
            created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            updated_at=datetime(2026, 1, 1, tzinfo=timezone.utc)
        )
        return self.token

    async def get_cart_token_by_token(self, token: str) -> Optional[CartTokenDTO]:
        """Return the stored token when it matches"""
        if self.token is not None and self.token.token == token:
            return self.token
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
