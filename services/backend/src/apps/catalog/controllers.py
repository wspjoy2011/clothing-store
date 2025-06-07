from dataclasses import asdict
from typing import Optional
from urllib.parse import urlencode

from fastapi import HTTPException

from apps.catalog.interfaces.services import CatalogServiceInterface
from apps.catalog.schemas.filters import FiltersResponseSchema, CheckboxFilterSchema, RangeFilterSchema
from apps.catalog.schemas.responses import (
    ProductListResponseSchema,
    ProductSchema,
    CategoryMenuResponseSchema,
    MasterCategorySchema,
    SubCategorySchema,
    ArticleTypeSchema
)


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


async def get_product_by_id_controller(
        product_id: int,
        catalog_service: CatalogServiceInterface,
) -> ProductSchema:
    """
    Controller for getting detailed information about a single product

    Args:
        product_id: The ID of the product to retrieve
        catalog_service: Catalog service for data access

    Returns:
        ProductSchema with detailed product information

    Raises:
        HTTPException: If product is not found (404)
    """
    product_dto = await catalog_service.get_product_by_id(product_id)

    if product_dto is None:
        raise HTTPException(
            status_code=404,
            detail=f"Product with ID {product_id} not found"
        )

    return ProductSchema(**asdict(product_dto))


async def get_filters_controller(
        catalog_service: CatalogServiceInterface,
        q: Optional[str] = None
) -> FiltersResponseSchema:
    """
    Get available filters for products

    Args:
        catalog_service: Catalog service for data access
        q: Optional search query to limit filters to relevant options

    Returns:
        Filters response schema

    Raises:
        HTTPException: If the catalog is empty
    """
    filters_dto = await catalog_service.get_available_filters(q)

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


async def get_category_menu_controller(
        catalog_service: CatalogServiceInterface
) -> CategoryMenuResponseSchema:
    """
    Controller for retrieving the category menu

    Args:
        catalog_service: Service for accessing catalog data

    Returns:
        Response schema with category hierarchy

    Raises:
        HTTPException: If no categories are available
    """
    category_menu = await catalog_service.get_category_menu()

    if not category_menu or not category_menu.categories:
        raise HTTPException(
            status_code=404,
            detail="No categories available in the catalog."
        )

    response_categories = []

    for master_category in category_menu.categories:
        response_sub_categories = []

        for sub_category in master_category.sub_categories:
            response_article_types = [
                ArticleTypeSchema(id=art_type.id, name=art_type.name)
                for art_type in sub_category.article_types
            ]

            response_sub_categories.append(SubCategorySchema(
                id=sub_category.id,
                name=sub_category.name,
                article_types=response_article_types
            ))

        response_categories.append(MasterCategorySchema(
            id=master_category.id,
            name=master_category.name,
            sub_categories=response_sub_categories
        ))

    return CategoryMenuResponseSchema(categories=response_categories)


async def get_products_by_category_controller(
        master_category_id: int,
        sub_category_id: Optional[int] = None,
        article_type_id: Optional[int] = None,
        page: int = 1,
        per_page: int = 10,
        ordering: Optional[str] = None,
        min_year: Optional[int] = None,
        max_year: Optional[int] = None,
        gender: Optional[str] = None,
        q: Optional[str] = None,
        catalog_service: CatalogServiceInterface = None,
) -> ProductListResponseSchema:
    """
    Controller for retrieving products filtered by category

    Args:
        master_category_id: ID of the master category (required)
        sub_category_id: ID of the sub-category (optional)
        article_type_id: ID of the article type (optional)
        page: Page number (1-based)
        per_page: Number of items per page
        ordering: Ordering string
        min_year: Minimum year filter
        max_year: Maximum year filter
        gender: Gender filter
        q: Search query
        catalog_service: Catalog service instance

    Returns:
        Response with products filtered by category
    """
    catalog_dto = await catalog_service.get_products_by_category(
        master_category_id=master_category_id,
        sub_category_id=sub_category_id,
        article_type_id=article_type_id,
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

    def build_url_with_params(page_num: int) -> str:
        base_path_parts = ["/api/v1/catalog/categories", str(master_category_id)]

        if sub_category_id:
            base_path_parts.append(str(sub_category_id))
            if article_type_id:
                base_path_parts.append(str(article_type_id))

        base_path_parts.append("products")
        base_url = "/".join(base_path_parts)

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


async def get_filters_by_categories_controller(
        master_category_id: int,
        sub_category_id: Optional[int] = None,
        article_type_id: Optional[int] = None,
        catalog_service: CatalogServiceInterface = None,
) -> FiltersResponseSchema:
    """
    Get available filters for products in specific categories

    Args:
        master_category_id: ID of the master category (required)
        sub_category_id: ID of the sub-category (optional)
        article_type_id: ID of the article type (optional)
        catalog_service: Catalog service for data access

    Returns:
        Filters response schema

    Raises:
        HTTPException: If no products found in the specified categories
    """
    filters_dto = await catalog_service.get_available_filters_by_categories(
        master_category_id=master_category_id,
        sub_category_id=sub_category_id,
        article_type_id=article_type_id
    )

    if filters_dto is None:
        raise HTTPException(
            status_code=404,
            detail="No products found in the specified categories. No filters available."
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


async def get_product_suggestions_controller(
        query: str,
        limit: int,
        catalog_service: CatalogServiceInterface,
) -> list[str]:
    """
    Controller for getting product name suggestions for autocomplete

    Args:
        query: Search query string
        limit: Maximum number of suggestions to return
        catalog_service: Catalog service for data access

    Returns:
        List of product name suggestions

    Raises:
        HTTPException: If query is too short or empty
    """
    if not query.strip():
        raise HTTPException(
            status_code=400,
            detail="Search query must be at least 1 character long"
        )

    return await catalog_service.get_product_suggestions(query.strip(), limit)
