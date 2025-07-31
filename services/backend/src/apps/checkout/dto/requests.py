from dataclasses import dataclass
from typing import Optional


@dataclass
class AddToCartRequestDTO:
    """Data transfer object for add to cart request"""
    product_id: int
    quantity: int = 1


@dataclass
class UpdateCartItemRequestDTO:
    """Data transfer object for update cart item request"""
    cart_item_id: int
    quantity: int
    cart_token: Optional[str] = None


@dataclass
class RemoveFromCartRequestDTO:
    """Data transfer object for remove from cart request"""
    cart_item_id: int
    cart_token: Optional[str] = None
