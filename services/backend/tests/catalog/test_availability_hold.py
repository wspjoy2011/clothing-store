from typing import Optional

from apps.catalog.dto.products import InventoryHoldDTO
from apps.catalog.services.catalog import CatalogService

PRODUCT_ID = 10


def hold(is_active: bool = True, is_in_stock: bool = True, available_quantity: int = 0) -> InventoryHoldDTO:
    """
    Build the state of one held inventory row

    Args:
        is_active: Whether the product is on sale
        is_in_stock: Whether the warehouse reports stock
        available_quantity: Units available for sale

    Returns:
        Held row state for the repository double to serve
    """
    return InventoryHoldDTO(
        is_active=is_active,
        is_in_stock=is_in_stock,
        available_quantity=available_quantity
    )


class FakeProductRepository:
    """Product repository serving one inventory row"""

    def __init__(self, inventory: Optional[InventoryHoldDTO]):
        self.inventory = inventory
        self.locked: list = []

    async def lock_inventory(self, product_id: int) -> Optional[InventoryHoldDTO]:
        """Record the lock request and return the configured row"""
        self.locked.append(product_id)
        return self.inventory


def build_service(inventory: Optional[InventoryHoldDTO]) -> CatalogService:
    """
    Assemble a catalog service around one inventory row

    Args:
        inventory: State of the held row, or None when there is none

    Returns:
        Service usable for availability checks
    """
    return CatalogService(
        product_repository=FakeProductRepository(inventory),
        category_repository=None,
        pagination_specification_factory=None,
        ordering_specification_factory=None,
        filter_specification_factory=None,
        search_specification_factory=None,
        category_specification_factory=None,
        autocomplete_client=None
    )


async def test_the_reported_quantity_is_the_sellable_one():
    """The hold reports what may be sold, leaving the decision to the caller"""
    service = build_service(hold(available_quantity=5))

    assert await service.hold_available_quantity(PRODUCT_ID) == 5


async def test_inactive_product_is_refused():
    """A product taken out of sale is refused even with stock on the shelf"""
    service = build_service(hold(is_active=False, available_quantity=100))

    assert await service.hold_available_quantity(PRODUCT_ID) is None


async def test_product_out_of_stock_is_refused():
    """A product marked out of stock is refused"""
    service = build_service(hold(is_in_stock=False, available_quantity=100))

    assert await service.hold_available_quantity(PRODUCT_ID) is None


async def test_product_without_inventory_is_refused():
    """A product with no inventory row cannot be held"""
    service = build_service(None)

    assert await service.hold_available_quantity(PRODUCT_ID) is None


async def test_the_inventory_row_is_locked():
    """The check goes through the locking read, not a plain one"""
    repository = FakeProductRepository(hold(available_quantity=5))
    service = CatalogService(
        product_repository=repository,
        category_repository=None,
        pagination_specification_factory=None,
        ordering_specification_factory=None,
        filter_specification_factory=None,
        search_specification_factory=None,
        category_specification_factory=None,
        autocomplete_client=None
    )

    await service.hold_available_quantity(PRODUCT_ID)

    assert repository.locked == [PRODUCT_ID]
