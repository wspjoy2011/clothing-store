from typing import Optional

from fastapi import APIRouter, Query, Depends

from apps.catalog.controllers import get_product_list_controller
from apps.catalog.dependencies import get_catalog_service
from apps.catalog.interfaces.services import CatalogServiceInterface
from apps.catalog.schemas.examples.responses import (
    STANDARD_RESPONSE_VALUE,
    YEAR_FILTERED_VALUE,
    GENDER_FILTERED_VALUE,
    YEAR_DESCENDING_VALUE,
    COMBINED_FILTERS_VALUE
)
from apps.catalog.schemas.responses import ProductListResponseSchema

router = APIRouter(
    prefix="/catalog",
    tags=["catalog"]
)


@router.get(
    f"/products",
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
