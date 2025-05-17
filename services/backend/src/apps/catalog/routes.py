from typing import Optional

from fastapi import APIRouter, Query, Depends

from apps.catalog.controllers import (
    get_product_list_controller,
    get_filters_controller
)
from apps.catalog.dependencies import get_catalog_service
from apps.catalog.interfaces.services import CatalogServiceInterface
from apps.catalog.schemas.examples.filters import FILTERS_FULL_EXAMPLE
from apps.catalog.schemas.examples.responses import (
    STANDARD_RESPONSE_VALUE,
    YEAR_FILTERED_VALUE,
    GENDER_FILTERED_VALUE,
    YEAR_DESCENDING_VALUE,
    COMBINED_FILTERS_VALUE
)
from apps.catalog.schemas.filters import FiltersResponseSchema
from apps.catalog.schemas.responses import ProductListResponseSchema

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
        "The response includes details about the products, total pages, and total items, "
        "along with links to the previous and next pages if applicable.</h3>"
    ),
    responses={
        404: {
            "description": "No products found.",
            "content": {
                "application/json": {
                    "example": {"detail": "No products found."}
                }
            },
        },
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
    catalog_service: CatalogServiceInterface = Depends(get_catalog_service),
):
    return await get_product_list_controller(
        page=page,
        per_page=per_page,
        ordering=ordering,
        min_year=min_year,
        max_year=max_year,
        gender=gender,
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
        catalog_service: CatalogServiceInterface = Depends(get_catalog_service)
) -> FiltersResponseSchema:
    """
    Get available filters for products

    This endpoint allows clients to fetch metadata about available filters that can be
    applied to the product catalog. The response contains filter structures with their
    respective type and possible values.

    If the catalog is empty, a 404 error is returned.

    Returns:
        FiltersResponseSchema: Object containing available filters

    Raises:
        404: If the catalog is empty, no filters are available
    """
    return await get_filters_controller(catalog_service)
