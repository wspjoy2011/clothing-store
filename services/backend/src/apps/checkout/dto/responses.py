from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional, List


@dataclass
class CartTokenResponseDTO:
    """Data transfer object for cart token response"""
    token: str
    expires_at: datetime


@dataclass
class CartItemResponseDTO:
    """Data transfer object for cart item in responses"""
    id: int
    product_id: int
    product_name: str
    product_slug: str
    product_image_url: str
    quantity: int
    unit_price: Decimal
    sale_price: Optional[Decimal]
    total_price: Decimal
    is_available: bool
    added_at: datetime


@dataclass
class CartResponseDTO:
    """Data transfer object for cart response"""
    id: int
    items: List[CartItemResponseDTO]
    total_items: int
    total_amount: Decimal
    total_discount: Decimal
    final_amount: Decimal
    created_at: datetime
    updated_at: datetime


@dataclass
class CartSummaryDTO:
    """Data transfer object for cart summary"""
    total_items: int
    total_amount: Decimal
    items_count: int
