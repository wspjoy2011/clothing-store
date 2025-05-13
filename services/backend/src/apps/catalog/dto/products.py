from dataclasses import dataclass


@dataclass
class ProductDTO:
    product_id: int
    gender: str
    year: int
    product_display_name: str
    image_url: str
