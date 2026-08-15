import pytest

from apps.checkout.dto.requests import AddToCartRequestDTO, UpdateCartItemRequestDTO
from apps.checkout.exceptions.services import CartNotFoundError, InsufficientStockError
from apps.checkout.services.cart import CartService
from tests.fakes import FakeTransactionManager
from tests.checkout.fakes import (
    FakeProduct,
    FakeCartItemRepository,
    FakeCartRepository,
    FakeCartTokenRepository,
    FakeCatalogService,
    build_cart_item,
)

USER_ID = 1


def build_service(
        catalog: FakeCatalogService,
        items: FakeCartItemRepository,
        transactions: FakeTransactionManager = None
) -> CartService:
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
        catalog_service=catalog,
        transaction_manager=transactions or FakeTransactionManager()
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

    assert catalog.holds == [42]


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

    assert catalog.holds == []
    assert items.updates == []


async def test_stock_is_held_inside_the_transaction_that_writes():
    """The availability check holds the inventory row within the writing transaction"""
    catalog = FakeCatalogService(available_quantity=5)
    items = FakeCartItemRepository(build_cart_item(quantity=1))
    transactions = FakeTransactionManager()
    service = build_service(catalog, items, transactions)

    await service.update_cart_item(
        UpdateCartItemRequestDTO(cart_item_id=1, quantity=3),
        user_id=USER_ID
    )

    assert catalog.holds_inside_transaction == [True]
    assert transactions.committed == 1


async def test_a_refused_hold_rolls_the_transaction_back():
    """A refused hold aborts the transaction instead of writing the quantity"""
    catalog = FakeCatalogService(available_quantity=2)
    items = FakeCartItemRepository(build_cart_item(quantity=1))
    transactions = FakeTransactionManager()
    service = build_service(catalog, items, transactions)

    with pytest.raises(InsufficientStockError):
        await service.update_cart_item(
            UpdateCartItemRequestDTO(cart_item_id=1, quantity=3),
            user_id=USER_ID
        )

    assert items.updates == []
    assert transactions.rolled_back == 1
    assert transactions.committed == 0


async def test_product_without_a_name_or_image_still_serves_the_cart():
    """A catalogue product missing optional fields does not break the cart response"""
    catalog = FakeCatalogService(
        available_quantity=5,
        product=FakeProduct(product_id=10, product_display_name=None, image_url=None, slug=None)
    )
    items = FakeCartItemRepository(build_cart_item(quantity=1))
    service = build_service(catalog, items)

    response = await service.update_cart_item(
        UpdateCartItemRequestDTO(cart_item_id=1, quantity=2),
        user_id=USER_ID
    )

    assert response.product_name == "Unknown Product"
    assert response.product_image_url == ""
    assert response.product_slug == "unknown"


async def test_item_of_another_cart_is_rejected_by_the_write():
    """An item that slips past the read but belongs elsewhere is refused by the write"""
    catalog = FakeCatalogService(available_quantity=5)
    items = FakeCartItemRepository(build_cart_item(quantity=1))
    service = build_service(catalog, items)

    items.item = build_cart_item(cart_id=999, quantity=1)

    with pytest.raises(CartNotFoundError):
        await service.update_cart_item(
            UpdateCartItemRequestDTO(cart_item_id=1, quantity=2),
            user_id=USER_ID
        )


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

    assert catalog.holds == []
    assert items.updates == []


async def test_adding_more_of_the_same_product_validates_the_total():
    """Adding to an item already in the cart checks the sum, not the increment"""
    catalog = FakeCatalogService(available_quantity=3)
    items = FakeCartItemRepository(build_cart_item(product_id=10, quantity=2))
    service = build_service(catalog, items)

    with pytest.raises(InsufficientStockError):
        await service.add_item_to_cart(
            AddToCartRequestDTO(product_id=10, quantity=2),
            user_id=USER_ID
        )

    assert catalog.holds == [10]


async def test_adding_within_the_total_is_stored():
    """A sum the warehouse can cover is added"""
    catalog = FakeCatalogService(available_quantity=3)
    items = FakeCartItemRepository(build_cart_item(product_id=10, quantity=2))
    service = build_service(catalog, items)

    response = await service.add_item_to_cart(
        AddToCartRequestDTO(product_id=10, quantity=1),
        user_id=USER_ID
    )

    assert response.quantity == 3
    assert catalog.holds == [10]
