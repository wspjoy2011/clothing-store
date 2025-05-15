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
        min_year: Optional[int],
        max_year: Optional[int],
        gender: Optional[str],
        catalog_service: CatalogServiceInterface,
) -> ProductListResponseSchema:
    catalog_dto = await catalog_service.get_products(
        page=page,
        per_page=per_page,
        ordering=ordering,
        min_year=min_year,
        max_year=max_year,
        gender=gender
    )

    if not catalog_dto.products:
        raise HTTPException(status_code=404, detail="No products found.")

    products = [ProductSchema(**asdict(product)) for product in catalog_dto.products]

    total_items = catalog_dto.pagination.total_items
    total_pages = catalog_dto.pagination.total_pages

    base_url = "/api/v1.0/catalog/products"

    def build_url_with_params(page_num: int) -> str:
        params = {'page': page_num, 'per_page': per_page}
        if ordering:
            params['ordering'] = ordering
        if min_year is not None:
            params['min_year'] = min_year
        if max_year is not None:
            params['max_year'] = max_year
        if gender:
            params['gender'] = gender
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
