from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass
class InventoryDTO:
    id: int
    product_id: int
    base_price: Decimal
    sale_price: Optional[Decimal]
    currency: str
    stock_quantity: int
    reserved_quantity: int
    available_quantity: int
    is_active: bool
    is_in_stock: bool
    created_at: datetime
    updated_at: datetime


@dataclass
class ProductDTO:
    product_id: int
    gender: str
    year: int
    product_display_name: str
    image_url: str
    slug: str
    inventory: Optional[InventoryDTO] = None
