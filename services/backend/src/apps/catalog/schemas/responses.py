from typing import Optional

from pydantic import BaseModel

from apps.catalog.schemas.examples.responses import (
    STANDARD_RESPONSE_VALUE,
    YEAR_FILTERED_VALUE,
    GENDER_FILTERED_VALUE,
    YEAR_DESCENDING_VALUE,
    COMBINED_FILTERS_VALUE
)


class ProductSchema(BaseModel):
    product_id: int
    gender: str
    year: int
    product_display_name: str
    image_url: str


class ProductListResponseSchema(BaseModel):
    products: list[ProductSchema]
    prev_page: Optional[str] = None
    next_page: Optional[str] = None
    total_pages: int
    total_items: int
