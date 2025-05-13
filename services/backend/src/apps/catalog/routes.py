from typing import Optional

from fastapi import APIRouter, Query, Depends

from apps.catalog.controllers import get_product_list_controller
from apps.catalog.dependencies import get_catalog_service
from apps.catalog.interfaces.services import CatalogServiceInterface
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
        "<h3>This endpoint retrieves a paginated list of products from the database. "
        "Clients can specify the `page` number and the number of items per page using `per_page`. "
        "Optional parameter `ordering` allows sorting results by fields with direction (e.g., 'year,-product_id'). "
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
    }
)
async def get_products_route(
    page: int = Query(1, ge=1, description="Page number (1-based index)"),
    per_page: int = Query(10, ge=1, le=20, description="Number of items per page"),
    ordering: Optional[str] = Query(None, description="Ordering fields (e.g., 'year,-product_id')"),
    catalog_service: CatalogServiceInterface = Depends(get_catalog_service),
):
    return await get_product_list_controller(
        page=page,
        per_page=per_page,
        ordering=ordering,
        catalog_service=catalog_service,
    )
