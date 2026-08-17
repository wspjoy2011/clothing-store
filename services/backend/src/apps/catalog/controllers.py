from typing import Optional
from urllib.parse import urlencode

from fastapi import HTTPException

from apps.catalog.dto.category import (
    ArticleTypeInfoDTO,
    CategoryMenuDTO,
    MasterCategoryInfoDTO,
    SubCategoryInfoDTO
)
from apps.catalog.dto.products import ProductDTO, InventoryDTO
from apps.catalog.interfaces.services import CatalogServiceInterface
from apps.catalog.schemas.filters import FiltersResponseSchema, CheckboxFilterSchema, RangeFilterSchema, \
    AvailabilityFilterSchema, PriceRangeFilterSchema
from apps.catalog.schemas.responses import (
    ProductListResponseSchema,
    ProductSchema,
    InventorySchema,
    CategoryMenuResponseSchema,
    MasterCategorySchema,
    SubCategorySchema,
    ArticleTypeSchema
)
from settings.api import CATALOG_CATEGORIES_PATH, CATALOG_PRODUCTS_PATH


def _convert_article_type_dto_to_schema(article_type: ArticleTypeInfoDTO) -> ArticleTypeSchema:
    """Convert ArticleTypeInfoDTO to ArticleTypeSchema"""
    return ArticleTypeSchema(id=article_type.id, name=article_type.name)


def _convert_sub_category_dto_to_schema(sub_category: SubCategoryInfoDTO) -> SubCategorySchema:
    """Convert SubCategoryInfoDTO to SubCategorySchema"""
    return SubCategorySchema(
        id=sub_category.id,
        name=sub_category.name,
        article_types=[
            _convert_article_type_dto_to_schema(article_type)
            for article_type in sub_category.article_types
        ]
    )


def _convert_master_category_dto_to_schema(master_category: MasterCategoryInfoDTO) -> MasterCategorySchema:
    """Convert MasterCategoryInfoDTO to MasterCategorySchema"""
    return MasterCategorySchema(
        id=master_category.id,
        name=master_category.name,
        sub_categories=[
            _convert_sub_category_dto_to_schema(sub_category)
            for sub_category in master_category.sub_categories
        ]
    )


def _convert_category_menu_dto_to_schema(category_menu: CategoryMenuDTO) -> CategoryMenuResponseSchema:
    """Convert CategoryMenuDTO to CategoryMenuResponseSchema"""
    return CategoryMenuResponseSchema(
        categories=[
            _convert_master_category_dto_to_schema(master_category)
            for master_category in category_menu.categories
        ]
    )


def _build_url_with_filters(
        base_url: str,
        page_num: int,
        per_page: int,
        ordering: Optional[str] = None,
        min_year: Optional[int] = None,
        max_year: Optional[int] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        gender: Optional[str] = None,
        is_available: Optional[bool] = None,
        q: Optional[str] = None
) -> str:
    """
    Build URL with query parameters for catalog endpoints

    Args:
        base_url: Base URL without query parameters
        page_num: Page number
        per_page: Items per page
        ordering: Ordering parameter
        min_year: Minimum year filter
        max_year: Maximum year filter
        min_price: Minimum price filter
        max_price: Maximum price filter
        gender: Gender filter
        is_available: Availability filter
        q: Search query

    Returns:
        Complete URL with query parameters
    """
    params = {'page': page_num, 'per_page': per_page}

    if ordering:
        params['ordering'] = ordering
    if min_year is not None:
        params['min_year'] = min_year
    if max_year is not None:
        params['max_year'] = max_year
    if min_price is not None:
        params['min_price'] = min_price
    if max_price is not None:
        params['max_price'] = max_price
    if gender:
        params['gender'] = gender
    if is_available is not None:
        params['is_available'] = is_available
    if q:
        params['q'] = q

    return f"{base_url}?{urlencode(params)}"


def _convert_inventory_dto_to_schema(inventory_dto: InventoryDTO) -> InventorySchema:
    """Convert InventoryDTO to InventorySchema"""
    return InventorySchema(
        id=inventory_dto.id,
        product_id=inventory_dto.product_id,
        base_price=inventory_dto.base_price,
        sale_price=inventory_dto.sale_price,
        currency=inventory_dto.currency,
        available_quantity=inventory_dto.available_quantity,
        is_active=inventory_dto.is_active,
        is_in_stock=inventory_dto.is_in_stock,
        created_at=inventory_dto.created_at,
        updated_at=inventory_dto.updated_at
    )


def _convert_product_dto_to_schema(product_dto: ProductDTO) -> ProductSchema:
    """Convert ProductDTO to ProductSchema with proper inventory conversion"""
    inventory_schema = None
    if product_dto.inventory:
        inventory_schema = _convert_inventory_dto_to_schema(product_dto.inventory)

    return ProductSchema(
        product_id=product_dto.product_id,
        gender=product_dto.gender,
        year=product_dto.year,
        product_display_name=product_dto.product_display_name,
        image_url=product_dto.image_url,
        slug=product_dto.slug,
        inventory=inventory_schema
    )


async def get_product_list_controller(
        page: int,
        per_page: int,
        ordering: Optional[str],
        min_year: Optional[int],
        max_year: Optional[int],
        min_price: Optional[float],
        max_price: Optional[float],
        gender: Optional[str],
        is_available: Optional[bool],
        q: Optional[str],
        catalog_service: CatalogServiceInterface,
) -> ProductListResponseSchema:
    catalog_dto = await catalog_service.get_products(
        page=page,
        per_page=per_page,
        ordering=ordering,
        min_year=min_year,
        max_year=max_year,
        min_price=min_price,
        max_price=max_price,
        gender=gender,
        is_available=is_available,
        q=q
    )

    products = [_convert_product_dto_to_schema(product) for product in catalog_dto.products]

    total_pages = catalog_dto.pagination.total_pages
    base_url = CATALOG_PRODUCTS_PATH

    prev_page = _build_url_with_filters(
        base_url, page - 1, per_page, ordering, min_year, max_year,
        min_price, max_price, gender, is_available, q
    ) if page > 1 else None

    next_page = _build_url_with_filters(
        base_url, page + 1, per_page, ordering, min_year, max_year,
        min_price, max_price, gender, is_available, q
    ) if page < total_pages else None

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

    return _convert_product_dto_to_schema(product_dto)


async def get_product_by_slug_controller(
        slug: str,
        catalog_service: CatalogServiceInterface,
) -> ProductSchema:
    """
    Controller for getting detailed information about a single product by slug

    Args:
        slug: The slug of the product to retrieve
        catalog_service: Catalog service for data access

    Returns:
        ProductSchema with detailed product information

    Raises:
        HTTPException: If product is not found (404)
    """
    product_dto = await catalog_service.get_product_by_slug(slug)

    if product_dto is None:
        raise HTTPException(
            status_code=404,
            detail=f"Product with slug '{slug}' not found"
        )

    return _convert_product_dto_to_schema(product_dto)


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
            values=filters_dto.gender.values,
            count=filters_dto.gender.count
        ) if filters_dto.gender else None,
        year=RangeFilterSchema(
            min=filters_dto.year.min,
            max=filters_dto.year.max
        ) if filters_dto.year else None,
        price=PriceRangeFilterSchema(
            min=filters_dto.price.min,
            max=filters_dto.price.max
        ) if filters_dto.price else None,
        is_available=AvailabilityFilterSchema(
            available_count=filters_dto.is_available.available_count,
            unavailable_count=filters_dto.is_available.unavailable_count
        ) if filters_dto.is_available else None
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

    return _convert_category_menu_dto_to_schema(category_menu)


async def get_products_by_category_controller(
        master_category_id: int,
        sub_category_id: Optional[int] = None,
        article_type_id: Optional[int] = None,
        page: int = 1,
        per_page: int = 10,
        ordering: Optional[str] = None,
        min_year: Optional[int] = None,
        max_year: Optional[int] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        gender: Optional[str] = None,
        is_available: Optional[bool] = None,
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
        min_price: Minimum price filter
        max_price: Maximum price filter
        gender: Gender filter
        is_available: Availability filter (True for available only, False for unavailable only)
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
        min_price=min_price,
        max_price=max_price,
        gender=gender,
        is_available=is_available,
        q=q
    )

    products = [_convert_product_dto_to_schema(product) for product in catalog_dto.products]

    total_pages = catalog_dto.pagination.total_pages

    base_path_parts = [CATALOG_CATEGORIES_PATH, str(master_category_id)]
    if sub_category_id:
        base_path_parts.append(str(sub_category_id))
        if article_type_id:
            base_path_parts.append(str(article_type_id))
    base_path_parts.append("products")
    base_url = "/".join(base_path_parts)

    prev_page = _build_url_with_filters(
        base_url, page - 1, per_page, ordering, min_year, max_year,
        min_price, max_price, gender, is_available, q
    ) if page > 1 else None

    next_page = _build_url_with_filters(
        base_url, page + 1, per_page, ordering, min_year, max_year,
        min_price, max_price, gender, is_available, q
    ) if page < total_pages else None

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
            values=filters_dto.gender.values,
            count=filters_dto.gender.count
        ) if filters_dto.gender else None,
        year=RangeFilterSchema(
            min=filters_dto.year.min,
            max=filters_dto.year.max
        ) if filters_dto.year else None,
        price=PriceRangeFilterSchema(
            min=filters_dto.price.min,
            max=filters_dto.price.max
        ) if filters_dto.price else None,
        is_available=AvailabilityFilterSchema(
            available_count=filters_dto.is_available.available_count,
            unavailable_count=filters_dto.is_available.unavailable_count
        ) if filters_dto.is_available else None
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
