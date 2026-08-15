from typing import Optional

from apps.catalog.services.catalog import CatalogService

PRODUCT_ID = 10


class FakeProductRepository:
    """Product repository serving one inventory row"""

    def __init__(self, inventory: Optional[tuple]):
        self.inventory = inventory
        self.locked: list = []

    async def lock_inventory(self, product_id: int) -> Optional[tuple]:
        """Record the lock request and return the configured row"""
        self.locked.append(product_id)
        return self.inventory


def build_service(inventory: Optional[tuple]) -> CatalogService:
    """
    Assemble a catalog service around one inventory row

    Args:
        inventory: is_active, is_in_stock and available_quantity, or None

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


async def test_available_stock_is_held():
    """Enough stock on an active product is confirmed"""
    service = build_service((True, True, 5))

    assert await service.hold_available_quantity(PRODUCT_ID) == 5


async def test_the_reported_quantity_is_the_sellable_one():
    """The hold reports what may be sold, leaving the decision to the caller"""
    service = build_service((True, True, 5))

    assert await service.hold_available_quantity(PRODUCT_ID) == 5


async def test_inactive_product_is_refused():
    """A product taken out of sale is refused even with stock on the shelf"""
    service = build_service((False, True, 100))

    assert await service.hold_available_quantity(PRODUCT_ID) is None


async def test_product_out_of_stock_is_refused():
    """A product marked out of stock is refused"""
    service = build_service((True, False, 100))

    assert await service.hold_available_quantity(PRODUCT_ID) is None


async def test_product_without_inventory_is_refused():
    """A product with no inventory row cannot be held"""
    service = build_service(None)

    assert await service.hold_available_quantity(PRODUCT_ID) is None


async def test_the_inventory_row_is_locked():
    """The check goes through the locking read, not a plain one"""
    repository = FakeProductRepository((True, True, 5))
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
