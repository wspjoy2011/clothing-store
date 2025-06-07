from typing import Optional

from fastapi import APIRouter, Query, Depends, Path

from apps.catalog.controllers import (
    get_product_list_controller,
    get_filters_controller,
    get_category_menu_controller,
    get_products_by_category_controller,
    get_filters_by_categories_controller,
    get_product_suggestions_controller,
    get_product_by_id_controller
)
from apps.catalog.dependencies import get_catalog_service
from apps.catalog.interfaces.services import CatalogServiceInterface
from apps.catalog.schemas.examples.filters import FILTERS_FULL_EXAMPLE
from apps.catalog.schemas.examples.responses import (
    STANDARD_RESPONSE_VALUE,
    YEAR_FILTERED_VALUE,
    GENDER_FILTERED_VALUE,
    YEAR_DESCENDING_VALUE,
    COMBINED_FILTERS_VALUE,
    CATEGORY_MENU_EXAMPLE,
    PRODUCT_EXAMPLE1
)
from apps.catalog.schemas.filters import FiltersResponseSchema
from apps.catalog.schemas.responses import (
    ProductListResponseSchema,
    CategoryMenuResponseSchema,
    ProductSchema
)

API_PATHS: dict[str, str] = {
    # Products
    "products": "/products",
    "product_by_id": "/products/{product_id}",
    "products_filters": "/products/filters",
    "products_suggestions": "/products/suggestions",

    # Categories
    "categories": "/categories",

    # Category-based products
    "products_by_master_category": "/categories/{master_category_id}/products",
    "products_by_subcategory": "/categories/{master_category_id}/{subcategory_id}/products",
    "products_by_article_type": "/categories/{master_category_id}/{subcategory_id}/{article_type_id}/products",

    # Category-based filters
    "filters_by_master_category": "/categories/{master_category_id}/filters",
    "filters_by_subcategory": "/categories/{master_category_id}/{subcategory_id}/filters",
    "filters_by_article_type": "/categories/{master_category_id}/{subcategory_id}/{article_type_id}/filters",
}

router = APIRouter(
    prefix="/catalog",
    tags=["catalog"]
)


@router.get(
    API_PATHS["products"],
    response_model=ProductListResponseSchema,
    status_code=200,
    summary="Get a paginated list of products",
    description=(
            "<h3>This endpoint retrieves a paginated and filtered list of products from the database. "
            "Clients can specify the `page` number and the number of items per page using `per_page`. "
            "Optional parameter `ordering` allows sorting results by fields with direction (e.g., 'year,-product_id'). "
            "Filtering is available by year range (`min_year`, `max_year`) and by gender (`gender`, which can be a comma-separated list). "
            "The search parameter `q` allows for full-text search in product names with results sorted by relevance. "
            "The response includes details about the products, total pages, and total items, "
            "along with links to the previous and next pages if applicable.</h3>"
    ),
    responses={
        422: {
            "description": "Validation error occurred for query parameters.",
            "content": {
                "application/json": {
                    "example": {
                        "field": "page",
                        "message": "value is not a valid integer"
                    }
                }
            },
        },
    },
    openapi_extra={
        "responses": {
            "200": {
                "content": {
                    "application/json": {
                        "examples": {
                            "standard": {
                                "summary": "Standard response",
                                "description": "Example response with default pagination",
                                "value": STANDARD_RESPONSE_VALUE
                            },
                            "year_filtered": {
                                "summary": "Filtered by year",
                                "description": "Example response when filtering by year range",
                                "value": YEAR_FILTERED_VALUE
                            },
                            "gender_filtered": {
                                "summary": "Filtered by gender",
                                "description": "Example response when filtering by gender",
                                "value": GENDER_FILTERED_VALUE
                            },
                            "year_descending": {
                                "summary": "Sorted by year (descending)",
                                "description": "Example response when sorting by year in descending order",
                                "value": YEAR_DESCENDING_VALUE
                            },
                            "combined_filters": {
                                "summary": "Combined filters and sorting",
                                "description": "Example response with both filtering and sorting",
                                "value": COMBINED_FILTERS_VALUE
                            }
                        }
                    }
                }
            }
        }
    }
)
async def get_products_route(
        page: int = Query(1, ge=1, description="Page number (1-based index)"),
        per_page: int = Query(10, ge=1, le=20, description="Number of items per page"),
        ordering: Optional[str] = Query(None, description="Ordering fields (e.g., 'year,-id')"),
        min_year: Optional[int] = Query(None, description="Minimum year filter (inclusive)"),
        max_year: Optional[int] = Query(None, description="Maximum year filter (inclusive)"),
        gender: Optional[str] = Query(None, description="Gender filter (comma-separated list, e.g., 'men,women')"),
        q: Optional[str] = Query(None, description="Search query for full-text search in product names"),
        catalog_service: CatalogServiceInterface = Depends(get_catalog_service),
):
    return await get_product_list_controller(
        page=page,
        per_page=per_page,
        ordering=ordering,
        min_year=min_year,
        max_year=max_year,
        gender=gender,
        q=q,
        catalog_service=catalog_service,
    )


@router.get(
    API_PATHS["product_by_id"],
    response_model=ProductSchema,
    status_code=200,
    summary="Get detailed product information by ID",
    description=(
            "<h3>This endpoint retrieves detailed information about a single product by its unique ID. "
            "Returns all available product data including name, gender, year, image URL, and slug. "
            "Use this endpoint to display product details on product pages or for any operations "
            "that require complete product information.</h3>"
    ),
    responses={
        404: {
            "description": "Product not found.",
            "content": {
                "application/json": {
                    "example": {"detail": "Product with ID 123 not found"}
                }
            },
        },
        422: {
            "description": "Validation error occurred for path parameters.",
            "content": {
                "application/json": {
                    "example": {
                        "field": "product_id",
                        "message": "value is not a valid integer"
                    }
                }
            },
        },
    },
    openapi_extra={
        "responses": {
            "200": {
                "content": {
                    "application/json": {
                        "examples": {
                            "product_detail": {
                                "summary": "Product details",
                                "description": "Example response with complete product information",
                                "value": PRODUCT_EXAMPLE1
                            }
                        }
                    }
                }
            }
        }
    }
)
async def get_product_by_id_route(
        product_id: int = Path(..., description="Unique identifier of the product", ge=1),
        catalog_service: CatalogServiceInterface = Depends(get_catalog_service),
):
    """
    Get detailed information about a single product by its ID

    Args:
        product_id: Unique identifier of the product
        catalog_service: Catalog service for data access

    Returns:
        ProductSchema: Complete product information

    Raises:
        HTTPException: 404 if product is not found, 422 for validation errors
    """
    return await get_product_by_id_controller(
        product_id=product_id,
        catalog_service=catalog_service,
    )


@router.get(
    API_PATHS["products_filters"],
    response_model=FiltersResponseSchema,
    status_code=200,
    summary="Get available product filters",
    description=(
            "<h3>This endpoint retrieves available filters for the product catalog based on the actual data. "
            "It provides information about available filter options such as gender values and year ranges. "
            "Clients can use this information to build dynamic filter UIs that adapt to the current catalog state. "
            "The endpoint returns filter metadata including possible values for checkbox filters and min/max ranges for "
            "numeric filters.</h3>"
    ),
    responses={
        404: {
            "description": "Catalog is empty, no filters available.",
            "content": {
                "application/json": {
                    "example": {"detail": "Catalog is empty. No filters available."}
                }
            },
        }
    },
    openapi_extra={
        "responses": {
            "200": {
                "content": {
                    "application/json": {
                        "examples": {
                            "full_filters": {
                                "summary": "Complete filters",
                                "description": "Example response with all filter types",
                                "value": FILTERS_FULL_EXAMPLE
                            },
                        }
                    }
                }
            }
        }
    }
)
async def filters_route(
        q: Optional[str] = Query(None, description="Optional search query to show only relevant filters"),
        catalog_service: CatalogServiceInterface = Depends(get_catalog_service)
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
    return await get_filters_controller(catalog_service, q)


@router.get(
    API_PATHS["categories"],
    response_model=CategoryMenuResponseSchema,
    status_code=200,
    summary="Get the complete category hierarchy",
    description=(
            "<h3>This endpoint retrieves the complete category hierarchy with all master categories, "
            "subcategories, and article types. The hierarchy is structured as a tree with three levels: "
            "master categories at the top level, subcategories as children of master categories, and "
            "article types as children of subcategories. This information can be used to build navigation menus, "
            "category browsers, or filtering interfaces in e-commerce applications.</h3>"
    ),
    responses={
        404: {
            "description": "No categories available.",
            "content": {
                "application/json": {
                    "example": {"detail": "No categories available in the catalog."}
                }
            },
        }
    },
    openapi_extra={
        "responses": {
            "200": {
                "content": {
                    "application/json": {
                        "examples": {
                            "category_menu": {
                                "summary": "Complete category hierarchy",
                                "description": "Example response with all category levels",
                                "value": CATEGORY_MENU_EXAMPLE
                            }
                        }
                    }
                }
            }
        }
    }
)
async def get_categories_route(
        catalog_service: CatalogServiceInterface = Depends(get_catalog_service)
) -> CategoryMenuResponseSchema:
    """
    Get the complete category hierarchy

    Args:
        catalog_service: Catalog service for data access

    Returns:
        Category menu with all hierarchy levels

    Raises:
        HTTPException: If no categories are available
    """
    return await get_category_menu_controller(catalog_service)


@router.get(
    API_PATHS["products_by_master_category"],
    response_model=ProductListResponseSchema,
    status_code=200,
    summary="Get products by category",
    description=(
            "<h3>This endpoint retrieves a paginated and filtered list of products from a specific category. "
            "The master_category_id is required to filter products by main category. "
            "All the filtering, sorting and pagination features from the /products endpoint are also available here, "
            "allowing for comprehensive data filtering based on your specific requirements.</h3>"
    ),
    responses={
        422: {
            "description": "Validation error occurred for query parameters.",
            "content": {
                "application/json": {
                    "example": {
                        "field": "page",
                        "message": "value is not a valid integer"
                    }
                }
            },
        },
    },
    openapi_extra={
        "responses": {
            "200": {
                "content": {
                    "application/json": {
                        "examples": {
                            "full_filters": {
                                "summary": "Complete filters",
                                "description": "Example response with all filter types",
                                "value": FILTERS_FULL_EXAMPLE
                            },
                        }
                    }
                }
            }
        }
    }
)
async def get_products_by_category_route(
        master_category_id: int = Path(..., description="ID of the master category"),
        page: int = Query(1, ge=1, description="Page number (1-based index)"),
        per_page: int = Query(10, ge=1, le=20, description="Number of items per page"),
        ordering: Optional[str] = Query(None, description="Ordering fields (e.g., 'year,-id')"),
        min_year: Optional[int] = Query(None, description="Minimum year filter (inclusive)"),
        max_year: Optional[int] = Query(None, description="Maximum year filter (inclusive)"),
        gender: Optional[str] = Query(None, description="Gender filter (comma-separated list, e.g., 'men,women')"),
        q: Optional[str] = Query(None, description="Search query for full-text search in product names"),
        catalog_service: CatalogServiceInterface = Depends(get_catalog_service),
):
    """
    Get products by category with pagination, filtering and sorting

    Args:
        master_category_id: ID of the master category (required)
        page: Page number
        per_page: Items per page
        ordering: Ordering string
        min_year: Minimum year filter
        max_year: Maximum year filter
        gender: Gender filter
        q: Search query
        catalog_service: Catalog service

    Returns:
        ProductListResponseSchema: List of products with pagination info
    """
    return await get_products_by_category_controller(
        master_category_id=master_category_id,
        sub_category_id=None,
        article_type_id=None,
        page=page,
        per_page=per_page,
        ordering=ordering,
        min_year=min_year,
        max_year=max_year,
        gender=gender,
        q=q,
        catalog_service=catalog_service,
    )


@router.get(
    API_PATHS["products_by_subcategory"],
    response_model=ProductListResponseSchema,
    status_code=200,
    summary="Get products by subcategory",
    description=(
            "<h3>This endpoint retrieves a paginated and filtered list of products from a specific subcategory. "
            "Both master_category_id and subcategory_id are required to filter products precisely. "
            "All the filtering, sorting and pagination features from the /products endpoint are also available here, "
            "allowing for comprehensive data filtering based on your specific requirements.</h3>"
    ),
    responses={
        422: {
            "description": "Validation error occurred for query parameters.",
            "content": {
                "application/json": {
                    "example": {
                        "field": "page",
                        "message": "value is not a valid integer"
                    }
                }
            },
        },
    },
    openapi_extra={
        "responses": {
            "200": {
                "content": {
                    "application/json": {
                        "examples": {
                            "full_filters": {
                                "summary": "Complete filters",
                                "description": "Example response with all filter types",
                                "value": FILTERS_FULL_EXAMPLE
                            },
                        }
                    }
                }
            }
        }
    }
)
async def get_products_by_subcategory_route(
        master_category_id: int = Path(..., description="ID of the master category"),
        subcategory_id: int = Path(..., description="ID of the subcategory"),
        page: int = Query(1, ge=1, description="Page number (1-based index)"),
        per_page: int = Query(10, ge=1, le=20, description="Number of items per page"),
        ordering: Optional[str] = Query(None, description="Ordering fields (e.g., 'year,-id')"),
        min_year: Optional[int] = Query(None, description="Minimum year filter (inclusive)"),
        max_year: Optional[int] = Query(None, description="Maximum year filter (inclusive)"),
        gender: Optional[str] = Query(None, description="Gender filter (comma-separated list, e.g., 'men,women')"),
        q: Optional[str] = Query(None, description="Search query for full-text search in product names"),
        catalog_service: CatalogServiceInterface = Depends(get_catalog_service),
):
    """
    Get products by subcategory with pagination, filtering and sorting

    Args:
        master_category_id: ID of the master category (required)
        subcategory_id: ID of the subcategory (required)
        page: Page number
        per_page: Items per-page
        ordering: Ordering string
        min_year: Minimum year filter
        max_year: Maximum year filter
        gender: Gender filter
        q: Search query
        catalog_service: Catalog service

    Returns:
        ProductListResponseSchema: List of products with pagination info
    """
    return await get_products_by_category_controller(
        master_category_id=master_category_id,
        sub_category_id=subcategory_id,
        article_type_id=None,
        page=page,
        per_page=per_page,
        ordering=ordering,
        min_year=min_year,
        max_year=max_year,
        gender=gender,
        q=q,
        catalog_service=catalog_service,
    )


@router.get(
    API_PATHS["products_by_article_type"],
    response_model=ProductListResponseSchema,
    status_code=200,
    summary="Get products by article type",
    description=(
            "<h3>This endpoint retrieves a paginated and filtered list of products from a specific article type. "
            "All three IDs (master_category_id, subcategory_id, and article_type_id) are required to filter products precisely. "
            "All the filtering, sorting and pagination features from the /products endpoint are also available here, "
            "allowing for comprehensive data filtering based on your specific requirements.</h3>"
    ),
    responses={
        422: {
            "description": "Validation error occurred for query parameters.",
            "content": {
                "application/json": {
                    "example": {
                        "field": "page",
                        "message": "value is not a valid integer"
                    }
                }
            },
        },
    },
    openapi_extra={
        "responses": {
            "200": {
                "content": {
                    "application/json": {
                        "examples": {
                            "full_filters": {
                                "summary": "Complete filters",
                                "description": "Example response with all filter types",
                                "value": FILTERS_FULL_EXAMPLE
                            },
                        }
                    }
                }
            }
        }
    }
)
async def get_products_by_article_type_route(
        master_category_id: int = Path(..., description="ID of the master category"),
        subcategory_id: int = Path(..., description="ID of the subcategory"),
        article_type_id: int = Path(..., description="ID of the article type"),
        page: int = Query(1, ge=1, description="Page number (1-based index)"),
        per_page: int = Query(10, ge=1, le=20, description="Number of items per page"),
        ordering: Optional[str] = Query(None, description="Ordering fields (e.g., 'year,-id')"),
        min_year: Optional[int] = Query(None, description="Minimum year filter (inclusive)"),
        max_year: Optional[int] = Query(None, description="Maximum year filter (inclusive)"),
        gender: Optional[str] = Query(None, description="Gender filter (comma-separated list, e.g., 'men,women')"),
        q: Optional[str] = Query(None, description="Search query for full-text search in product names"),
        catalog_service: CatalogServiceInterface = Depends(get_catalog_service),
):
    """
    Get products by article type with pagination, filtering and sorting

    Args:
        master_category_id: ID of the master category (required)
        subcategory_id: ID of the subcategory (required)
        article_type_id: ID of the article type (required)
        page: Page number
        per_page: Items per-page
        ordering: Ordering string
        min_year: Minimum year filter
        max_year: Maximum year filter
        gender: Gender filter
        q: Search query
        catalog_service: Catalog service

    Returns:
        ProductListResponseSchema: List of products with pagination info
    """
    return await get_products_by_category_controller(
        master_category_id=master_category_id,
        sub_category_id=subcategory_id,
        article_type_id=article_type_id,
        page=page,
        per_page=per_page,
        ordering=ordering,
        min_year=min_year,
        max_year=max_year,
        gender=gender,
        q=q,
        catalog_service=catalog_service,
    )


@router.get(
    API_PATHS["filters_by_master_category"],
    response_model=FiltersResponseSchema,
    status_code=200,
    summary="Get available filters for master category",
    description=(
            "<h3>This endpoint retrieves available filters for products in a specific master category. "
            "It provides information about available filter options such as gender values and year ranges "
            "based only on products within the specified master category. "
            "Clients can use this information to build dynamic filter UIs that adapt to the current category state.</h3>"
    ),
    responses={
        404: {
            "description": "No products found in the specified category.",
            "content": {
                "application/json": {
                    "example": {"detail": "No products found in the specified categories. No filters available."}
                }
            },
        }
    },
    openapi_extra={
        "responses": {
            "200": {
                "content": {
                    "application/json": {
                        "examples": {
                            "full_filters": {
                                "summary": "Complete filters for category",
                                "description": "Example response with all filter types for specific category",
                                "value": FILTERS_FULL_EXAMPLE
                            },
                        }
                    }
                }
            }
        }
    }
)
async def get_filters_by_master_category_route(
        master_category_id: int = Path(..., description="ID of the master category"),
        catalog_service: CatalogServiceInterface = Depends(get_catalog_service)
) -> FiltersResponseSchema:
    """
    Get available filters for products in master category

    Args:
        master_category_id: ID of the master category (required)
        catalog_service: Catalog service for data access

    Returns:
        Filters response schema

    Raises:
        HTTPException: If no products found in the specified category
    """
    return await get_filters_by_categories_controller(
        master_category_id=master_category_id,
        catalog_service=catalog_service
    )


@router.get(
    API_PATHS["filters_by_subcategory"],
    response_model=FiltersResponseSchema,
    status_code=200,
    summary="Get available filters for subcategory",
    description=(
            "<h3>This endpoint retrieves available filters for products in a specific subcategory. "
            "It provides information about available filter options such as gender values and year ranges "
            "based only on products within the specified subcategory. "
            "Clients can use this information to build dynamic filter UIs that adapt to the current subcategory state.</h3>"
    ),
    responses={
        404: {
            "description": "No products found in the specified subcategory.",
            "content": {
                "application/json": {
                    "example": {"detail": "No products found in the specified categories. No filters available."}
                }
            },
        }
    },
    openapi_extra={
        "responses": {
            "200": {
                "content": {
                    "application/json": {
                        "examples": {
                            "full_filters": {
                                "summary": "Complete filters for subcategory",
                                "description": "Example response with all filter types for specific subcategory",
                                "value": FILTERS_FULL_EXAMPLE
                            },
                        }
                    }
                }
            }
        }
    }
)
async def get_filters_by_subcategory_route(
        master_category_id: int = Path(..., description="ID of the master category"),
        subcategory_id: int = Path(..., description="ID of the subcategory"),
        catalog_service: CatalogServiceInterface = Depends(get_catalog_service)
) -> FiltersResponseSchema:
    """
    Get available filters for products in subcategory

    Args:
        master_category_id: ID of the master category (required)
        subcategory_id: ID of the subcategory (required)
        catalog_service: Catalog service for data access

    Returns:
        Filters response schema

    Raises:
        HTTPException: If no products found in the specified subcategory
    """
    return await get_filters_by_categories_controller(
        master_category_id=master_category_id,
        sub_category_id=subcategory_id,
        catalog_service=catalog_service
    )


@router.get(
    API_PATHS["filters_by_article_type"],
    response_model=FiltersResponseSchema,
    status_code=200,
    summary="Get available filters for article type",
    description=(
            "<h3>This endpoint retrieves available filters for products in a specific article type. "
            "It provides information about available filter options such as gender values and year ranges "
            "based only on products within the specified article type. "
            "Clients can use this information to build dynamic filter UIs that adapt to the current article type state.</h3>"
    ),
    responses={
        404: {
            "description": "No products found in the specified article type.",
            "content": {
                "application/json": {
                    "example": {"detail": "No products found in the specified categories. No filters available."}
                }
            },
        }
    },
    openapi_extra={
        "responses": {
            "200": {
                "content": {
                    "application/json": {
                        "examples": {
                            "full_filters": {
                                "summary": "Complete filters for article type",
                                "description": "Example response with all filter types for specific article type",
                                "value": FILTERS_FULL_EXAMPLE
                            },
                        }
                    }
                }
            }
        }
    }
)
async def get_filters_by_article_type_route(
        master_category_id: int = Path(..., description="ID of the master category"),
        subcategory_id: int = Path(..., description="ID of the subcategory"),
        article_type_id: int = Path(..., description="ID of the article type"),
        catalog_service: CatalogServiceInterface = Depends(get_catalog_service)
) -> FiltersResponseSchema:
    """
    Get available filters for products in article type

    Args:
        master_category_id: ID of the master category (required)
        subcategory_id: ID of the subcategory (required)
        article_type_id: ID of the article type (required)
        catalog_service: Catalog service for data access

    Returns:
        Filters response schema

    Raises:
        HTTPException: If no products found in the specified article type
    """
    return await get_filters_by_categories_controller(
        master_category_id=master_category_id,
        sub_category_id=subcategory_id,
        article_type_id=article_type_id,
        catalog_service=catalog_service
    )


@router.get(
    API_PATHS["products_suggestions"],
    response_model=list[str],
    summary="Get product name suggestions",
    description="Get product name suggestions for autocomplete functionality"
)
async def get_product_suggestions_route(
        q: str = Query(
            ...,
            description="Search query for product suggestions",
            min_length=1,
            max_length=50,
            example="N"
        ),
        limit: int = Query(
            10,
            description="Maximum number of suggestions to return",
            ge=1,
            le=20,
            example=10
        ),
        catalog_service: CatalogServiceInterface = Depends(get_catalog_service)
) -> list[str]:
    """
    Get product name suggestions for autocomplete.

    Returns a list of product names that match the search query.
    Useful for implementing search autocomplete functionality.
    Searches from 1 character minimum.
    """
    return await get_product_suggestions_controller(
        query=q,
        limit=limit,
        catalog_service=catalog_service
    )
