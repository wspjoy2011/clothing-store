from datetime import datetime, timezone
from decimal import Decimal

from apps.catalog.repositories.product import ProductRepository

CREATED = datetime(2026, 1, 1, tzinfo=timezone.utc)


def build_row(year=2026, display_name="Test Product", image_url="http://example.com/i.jpg", with_inventory=True):
    """
    Build a catalogue row as the database returns it

    Args:
        year: Release year, nullable in the table
        display_name: Product name, nullable in the table
        image_url: Image address, nullable in the table
        with_inventory: Whether the row carries the joined inventory columns

    Returns:
        Row tuple accepted by the mapper
    """
    product = (1, "Unisex", year, display_name, image_url, "1-test-product")
    if not with_inventory:
        return product + (None,) * 11

    return product + (
        7, Decimal("10.00"), None, "USD", 5, 0, 5, True, True, CREATED, CREATED
    )


def build_repository() -> ProductRepository:
    """
    Build a repository without touching the database

    Returns:
        Repository usable for row mapping only
    """
    return ProductRepository(dao=None, query_builder=None)


def test_row_with_every_field_is_mapped():
    """A complete row keeps all of its values"""
    product = build_repository()._build_product_dto_from_row(build_row())

    assert product.product_id == 1
    assert product.year == 2026
    assert product.product_display_name == "Test Product"
    assert product.inventory.available_quantity == 5


def test_row_without_a_year_is_mapped():
    """A product with no release year does not break the listing"""
    product = build_repository()._build_product_dto_from_row(build_row(year=None))

    assert product.year is None
    assert product.product_id == 1


def test_row_without_a_name_or_image_is_mapped():
    """A product missing its name or image is still returned"""
    product = build_repository()._build_product_dto_from_row(
        build_row(display_name=None, image_url=None)
    )

    assert product.product_display_name is None
    assert product.image_url is None


def test_row_without_inventory_is_mapped():
    """A product that has no inventory row carries no inventory"""
    product = build_repository()._build_product_dto_from_row(build_row(with_inventory=False))

    assert product.inventory is None
