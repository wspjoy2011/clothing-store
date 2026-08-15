import pytest
from pydantic import ValidationError

from apps.catalog.schemas.responses import ProductSchema

COMPLETE = {
    "product_id": 1,
    "gender": "Unisex",
    "year": 2026,
    "product_display_name": "Test Product",
    "image_url": "http://example.com/i.jpg",
    "slug": "1-test-product",
}


def test_complete_product_is_accepted():
    """A product carrying every field validates"""
    product = ProductSchema(**COMPLETE)

    assert product.year == 2026
    assert product.product_display_name == "Test Product"


def test_product_without_optional_fields_is_accepted():
    """The fields nullable in the table are accepted as null at the HTTP edge"""
    product = ProductSchema(**{**COMPLETE, "year": None, "product_display_name": None, "image_url": None})

    assert product.year is None
    assert product.product_display_name is None
    assert product.image_url is None


def test_product_without_a_slug_is_rejected():
    """Slug is not nullable in the table and stays required here"""
    payload = {key: value for key, value in COMPLETE.items() if key != "slug"}

    with pytest.raises(ValidationError):
        ProductSchema(**payload)
