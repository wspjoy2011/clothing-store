from typing import Optional

from pydantic import BaseModel, HttpUrl


class ProductSchema(BaseModel):
    product_id: int
    gender: str
    year: int
    product_display_name: str
    image_url: HttpUrl


class ProductListResponseSchema(BaseModel):
    products: list[ProductSchema]
    prev_page: Optional[str]
    next_page: Optional[str]
    total_pages: int
    total_items: int

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "products": [
                        {
                            "product_id": 1,
                            "gender": "Men",
                            "year": 2023,
                            "product_display_name": "Running Shoes",
                            "image_url": "https://example.com/product1.jpg",
                        },
                        {
                            "product_id": 2,
                            "gender": "Women",
                            "year": 2022,
                            "product_display_name": "Comfortable Sandals",
                            "image_url": "https://example.com/product2.jpg",
                        },
                    ],
                    "prev_page": "/api/v1.0/catalog/products?page=1",
                    "next_page": "/api/v1.0/catalog/products?page=3",
                    "total_pages": 10,
                    "total_items": 100,
                }
            ]
        }
    }
