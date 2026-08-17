from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class CartDTO:
    """Data transfer object for shopping cart"""
    id: int
    user_id: Optional[int]
    cart_token_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    items: Optional[List['CartItemDTO']] = None


@dataclass
class CartItemDTO:
    """Data transfer object for cart item"""
    id: int
    cart_id: int
    product_id: int
    quantity: int
    added_at: datetime
    updated_at: datetime
    product: Optional[dict] = None
