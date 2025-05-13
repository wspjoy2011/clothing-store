from dataclasses import asdict
from typing import Optional
from urllib.parse import urlencode

from fastapi import HTTPException

from apps.catalog.interfaces.services import CatalogServiceInterface
from apps.catalog.schemas.responses import ProductListResponseSchema, ProductSchema


async def get_product_list_controller(
        page: int,
        per_page: int,
        ordering: Optional[str],
        catalog_service: CatalogServiceInterface,
) -> ProductListResponseSchema:
    products = await catalog_service.get_paginated_products(page, per_page, ordering)

    if products is None:
        raise HTTPException(status_code=404, detail="No products found.")

    products = [ProductSchema(**asdict(product)) for product in products]

    total_items = await catalog_service.get_products_count()
    total_pages = (total_items + per_page - 1) // per_page

    base_url = "/api/v1.0/catalog/products"

    def build_url_with_params(page_num: int) -> str:
        params = {'page': page_num, 'per_page': per_page}
        if ordering:
            params['ordering'] = ordering
        return f"{base_url}?{urlencode(params)}"

    prev_page = build_url_with_params(page - 1) if page > 1 else None
    next_page = build_url_with_params(page + 1) if page < total_pages else None

    return ProductListResponseSchema(
        products=products,
        prev_page=prev_page,
        next_page=next_page,
        total_pages=total_pages,
        total_items=total_items,
    )
