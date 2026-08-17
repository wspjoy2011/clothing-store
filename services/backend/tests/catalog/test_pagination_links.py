from datetime import datetime, timezone
from decimal import Decimal
from urllib.parse import urlparse

import pytest
from fastapi.testclient import TestClient

from apps.catalog.dependencies import get_catalog_service
from apps.catalog.dto.catalog import CatalogDTO, PaginationDTO
from apps.catalog.dto.products import InventoryDTO, ProductDTO
from main import app
from settings.api import CATALOG_CATEGORIES_PATH, CATALOG_PRODUCTS_PATH

TOTAL_PAGES = 3


def build_product() -> ProductDTO:
    """
    Build one listed product

    Navigation links are only returned alongside products, so a listing has to
    carry at least one for the links to be there at all.

    Returns:
        Product complete enough for the listing response
    """
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    return ProductDTO(
        product_id=1,
        gender="Men",
        year=2020,
        product_display_name="Test Shirt",
        image_url="http://example.com/shirt.jpg",
        slug="test-shirt",
        inventory=InventoryDTO(
            id=1,
            product_id=1,
            base_price=Decimal("10.00"),
            sale_price=None,
            currency="USD",
            stock_quantity=5,
            reserved_quantity=0,
            available_quantity=5,
            is_active=True,
            is_in_stock=True,
            created_at=now,
            updated_at=now
        )
    )


class FakeCatalogService:
    """Catalog service answering with one page of a multi-page listing"""

    async def get_products(self, **kwargs) -> CatalogDTO:
        """Report a listing long enough to carry navigation links"""
        return CatalogDTO(
            products=[build_product()],
            pagination=PaginationDTO(
                page=kwargs.get("page", 1),
                per_page=kwargs.get("per_page", 10),
                total_items=TOTAL_PAGES * 10,
                total_pages=TOTAL_PAGES
            )
        )


@pytest.fixture
def client() -> TestClient:
    """Serve the application with a catalog that needs no database"""
    app.dependency_overrides[get_catalog_service] = lambda: FakeCatalogService()
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def mounted_paths() -> set:
    """
    Collect the paths the application actually serves

    Returns:
        Every route path registered on the application
    """
    return {route.path for route in app.routes}


def test_the_next_page_link_points_at_a_served_path(client):
    """The link the listing hands the client resolves to a route that exists"""
    body = client.get(f"{CATALOG_PRODUCTS_PATH}?page=1&per_page=10").json()

    next_path = urlparse(body["next_page"]).path

    assert next_path in mounted_paths()


def test_the_previous_page_link_points_at_a_served_path(client):
    """The backward link resolves as well, not only the forward one"""
    body = client.get(f"{CATALOG_PRODUCTS_PATH}?page=2&per_page=10").json()

    previous_path = urlparse(body["prev_page"]).path

    assert previous_path in mounted_paths()


def test_following_the_next_page_link_answers(client):
    """Walking the link the API returned reaches the listing instead of a 404"""
    body = client.get(f"{CATALOG_PRODUCTS_PATH}?page=1&per_page=10").json()

    followed = client.get(body["next_page"])

    assert followed.status_code == 200


def test_the_category_listing_links_point_at_a_served_path():
    """Category pagination links are built from a path the application serves"""
    assert any(path.startswith(CATALOG_CATEGORIES_PATH) for path in mounted_paths())


def test_the_public_product_response_hides_warehouse_counts(client):
    """Stock and reservation figures are ours, not the anonymous caller's"""
    body = client.get(f"{CATALOG_PRODUCTS_PATH}?page=1&per_page=1").json()

    inventory = body["products"][0]["inventory"]

    assert "stock_quantity" not in inventory
    assert "reserved_quantity" not in inventory
    assert inventory["available_quantity"] == 5
