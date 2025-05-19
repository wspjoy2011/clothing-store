from dataclasses import asdict
from typing import Optional
from urllib.parse import urlencode

from fastapi import HTTPException

from apps.catalog.interfaces.services import CatalogServiceInterface
from apps.catalog.schemas.filters import FiltersResponseSchema, CheckboxFilterSchema, RangeFilterSchema
from apps.catalog.schemas.responses import ProductListResponseSchema, ProductSchema


async def get_product_list_controller(
        page: int,
        per_page: int,
        ordering: Optional[str],
        min_year: Optional[int],
        max_year: Optional[int],
        gender: Optional[str],
        q: Optional[str],
        catalog_service: CatalogServiceInterface,
) -> ProductListResponseSchema:
    catalog_dto = await catalog_service.get_products(
        page=page,
        per_page=per_page,
        ordering=ordering,
        min_year=min_year,
        max_year=max_year,
        gender=gender,
        q=q
    )

    products = [ProductSchema(**asdict(product)) for product in catalog_dto.products]

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
        if q:
            params['q'] = q
        return f"{base_url}?{urlencode(params)}"

    prev_page = build_url_with_params(page - 1) if page > 1 else None
    next_page = build_url_with_params(page + 1) if page < total_pages else None

    return ProductListResponseSchema(
        products=products,
        prev_page=None if not products else prev_page,
        next_page=None if not products else next_page,
        total_pages=catalog_dto.pagination.total_pages,
        total_items=catalog_dto.pagination.total_items,
    )


async def get_filters_controller(
        catalog_service: CatalogServiceInterface,
) -> FiltersResponseSchema:
    """
    Get available filters for products

    Args:
        catalog_service: Catalog service for data access

    Returns:
        Filters response schema

    Raises:
        HTTPException: If the catalog is empty
    """
    filters_dto = await catalog_service.get_available_filters()

    if filters_dto is None:
        raise HTTPException(
            status_code=404,
            detail="Catalog is empty. No filters available."
        )

    return FiltersResponseSchema(
        gender=CheckboxFilterSchema(
            values=filters_dto.gender.values
        ) if filters_dto.gender else None,
        year=RangeFilterSchema(
            min=filters_dto.year.min,
            max=filters_dto.year.max
        ) if filters_dto.year else None
    )
