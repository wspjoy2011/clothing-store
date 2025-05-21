from typing import Optional

from fastapi import APIRouter, Query, Depends

from apps.catalog.controllers import (
    get_product_list_controller,
    get_filters_controller,
    get_category_menu_controller
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
    CATEGORY_MENU_EXAMPLE
)
from apps.catalog.schemas.filters import FiltersResponseSchema
from apps.catalog.schemas.responses import ProductListResponseSchema, CategoryMenuResponseSchema

router = APIRouter(
    prefix="/catalog",
    tags=["catalog"]
)


@router.get(
    "/products",
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
    "/products/filters",
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
    "/categories",
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
