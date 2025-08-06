from typing import Optional

from pydantic import BaseModel, Field


class GetCartByTokenRequest(BaseModel):
    """Schema for getting cart by token request"""
    token: str = Field(..., description="Cart token for anonymous users")

    class Config:
        json_schema_extra = {
            "example": {
                "token": "abc123def456ghi789jkl012"
            }
        }


class AddToCartRequest(BaseModel):
    """Schema for add to cart request"""
    product_id: int = Field(..., gt=0, description="ID of the product to add")
    quantity: int = Field(1, ge=1, le=999, description="Quantity to add")

    class Config:
        json_schema_extra = {
            "example": {
                "product_id": 123,
                "quantity": 2,
            }
        }


class UpdateCartItemRequest(BaseModel):
    """Schema for update cart item request"""
    cart_item_id: int = Field(..., gt=0, description="ID of the cart item to update")
    quantity: int = Field(..., ge=1, le=999, description="New quantity")

    class Config:
        json_schema_extra = {
            "example": {
                "cart_item_id": 456,
                "quantity": 3,
                "cart_token": "abc123def456..."
            }
        }


class RemoveFromCartRequest(BaseModel):
    """Schema for remove from cart request"""
    cart_item_id: int = Field(..., gt=0, description="ID of the cart item to remove")
    cart_token: Optional[str] = Field(None, description="Cart token for anonymous users")

    class Config:
        json_schema_extra = {
            "example": {
                "cart_item_id": 456,
                "cart_token": "abc123def456..."
            }
        }
