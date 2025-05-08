from dataclasses import asdict

from fastapi import HTTPException

from apps.catalog.interfaces.services import CatalogServiceInterface
from apps.catalog.schemas.responses import ProductListResponseSchema, ProductSchema


async def get_product_list_controller(
        page: int,
        per_page: int,
        catalog_service: CatalogServiceInterface,
) -> ProductListResponseSchema:
    products = await catalog_service.get_paginated_products(page, per_page)

    if products is None:
        raise HTTPException(status_code=404, detail="No products found.")

    products = [ProductSchema(**asdict(product)) for product in products]

    total_items = await catalog_service.get_products_count()
    total_pages = (total_items + per_page - 1) // per_page

    base_url = "/api/v1.0/catalog/products"
    prev_page = f"{base_url}?page={page - 1}&per_page={per_page}" if page > 1 else None
    next_page = f"{base_url}?page={page + 1}&per_page={per_page}" if page < total_pages else None

    return ProductListResponseSchema(
        products=products,
        prev_page=prev_page,
        next_page=next_page,
        total_pages=total_pages,
        total_items=total_items,
    )
