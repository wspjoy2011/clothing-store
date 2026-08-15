import pytest

from apps.checkout.dto.requests import UpdateCartItemRequestDTO
from apps.checkout.exceptions.services import CartNotFoundError, InsufficientStockError
from apps.checkout.services.cart import CartService
from tests.checkout.fakes import (
    FakeCartItemRepository,
    FakeCartRepository,
    FakeCartTokenRepository,
    FakeCatalogService,
    build_cart_item,
)

USER_ID = 1


def build_service(catalog: FakeCatalogService, items: FakeCartItemRepository) -> CartService:
    """
    Assemble a cart service from test doubles

    Args:
        catalog: Catalog reporting stock
        items: Repository holding the cart item

    Returns:
        Service wired for the test
    """
    return CartService(
        cart_token_repository=FakeCartTokenRepository(),
        cart_repository=FakeCartRepository(),
        cart_item_repository=items,
        catalog_service=catalog
    )


async def test_quantity_within_stock_is_applied():
    """A quantity the warehouse can cover is stored"""
    catalog = FakeCatalogService(available_quantity=5)
    items = FakeCartItemRepository(build_cart_item(quantity=1))
    service = build_service(catalog, items)

    response = await service.update_cart_item(
        UpdateCartItemRequestDTO(cart_item_id=1, quantity=3),
        user_id=USER_ID
    )

    assert response.quantity == 3
    assert items.updates == [(1, 3, 1)]


async def test_quantity_beyond_stock_is_rejected():
    """A quantity larger than the available stock never reaches the database"""
    catalog = FakeCatalogService(available_quantity=2)
    items = FakeCartItemRepository(build_cart_item(quantity=1))
    service = build_service(catalog, items)

    with pytest.raises(InsufficientStockError):
        await service.update_cart_item(
            UpdateCartItemRequestDTO(cart_item_id=1, quantity=3),
            user_id=USER_ID
        )

    assert items.updates == []


async def test_stock_is_checked_for_the_product_of_that_item():
    """Availability is checked against the product the item refers to"""
    catalog = FakeCatalogService(available_quantity=10)
    items = FakeCartItemRepository(build_cart_item(product_id=42, quantity=1))
    service = build_service(catalog, items)

    await service.update_cart_item(
        UpdateCartItemRequestDTO(cart_item_id=1, quantity=4),
        user_id=USER_ID
    )

    assert catalog.availability_checks == [(42, 4)]


async def test_item_of_another_cart_is_not_updated():
    """An item belonging to a different cart is rejected before any stock check"""
    catalog = FakeCatalogService(available_quantity=100)
    items = FakeCartItemRepository(build_cart_item(cart_id=999, quantity=1))
    service = build_service(catalog, items)

    with pytest.raises(CartNotFoundError):
        await service.update_cart_item(
            UpdateCartItemRequestDTO(cart_item_id=1, quantity=2),
            user_id=USER_ID
        )

    assert catalog.availability_checks == []
    assert items.updates == []


async def test_stock_taken_between_check_and_write_is_refused():
    """Losing the race against another request is reported as missing stock, not as success"""
    catalog = FakeCatalogService(available_quantity=5)
    items = FakeCartItemRepository(build_cart_item(quantity=1), available_quantity=0)
    service = build_service(catalog, items)

    with pytest.raises(InsufficientStockError):
        await service.update_cart_item(
            UpdateCartItemRequestDTO(cart_item_id=1, quantity=3),
            user_id=USER_ID
        )

    assert items.updates == [(1, 3, 1)]


async def test_missing_item_is_rejected():
    """An unknown item is rejected before any stock check"""
    catalog = FakeCatalogService(available_quantity=100)
    items = FakeCartItemRepository(item=None)
    service = build_service(catalog, items)

    with pytest.raises(CartNotFoundError):
        await service.update_cart_item(
            UpdateCartItemRequestDTO(cart_item_id=1, quantity=2),
            user_id=USER_ID
        )

    assert catalog.availability_checks == []
    assert items.updates == []
