from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field


class CartTokenResponse(BaseModel):
    """Schema for cart token response"""
    token: str = Field(..., description="Unique cart token")
    expires_at: datetime = Field(..., description="Token expiration date")

    class Config:
        json_schema_extra = {
            "example": {
                "token": "abc123def456ghi789jkl012",
                "expires_at": "2025-07-30T12:00:00Z"
            }
        }


class CartItemResponse(BaseModel):
    """Schema for cart item in responses"""
    id: int = Field(..., description="Cart item ID")
    product_id: int = Field(..., description="Product ID")
    product_name: str = Field(..., description="Product display name")
    product_slug: str = Field(..., description="Product URL slug")
    product_image_url: str = Field(..., description="Product image URL")
    quantity: int = Field(..., ge=1, description="Item quantity")
    unit_price: Decimal = Field(..., ge=0, description="Unit price")
    sale_price: Optional[Decimal] = Field(None, ge=0, description="Sale price if available")
    total_price: Decimal = Field(..., ge=0, description="Total price for this item")
    is_available: bool = Field(..., description="Item availability status")
    added_at: datetime = Field(..., description="When item was added to cart")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 123,
                "product_id": 456,
                "product_name": "Premium T-Shirt",
                "product_slug": "premium-t-shirt",
                "product_image_url": "https://example.com/images/tshirt.jpg",
                "quantity": 2,
                "unit_price": "29.99",
                "sale_price": "24.99",
                "total_price": "49.98",
                "is_available": True,
                "added_at": "2025-07-29T10:30:00Z"
            }
        }


class CartResponse(BaseModel):
    """Schema for cart response"""
    id: int = Field(..., description="Cart ID")
    items: List[CartItemResponse] = Field([], description="List of cart items")
    total_items: int = Field(..., ge=0, description="Total number of items")
    total_amount: Decimal = Field(..., ge=0, description="Total amount before discounts")
    total_discount: Decimal = Field(..., ge=0, description="Total discount amount")
    final_amount: Decimal = Field(..., ge=0, description="Final amount after discounts")
    created_at: datetime = Field(..., description="Cart creation date")
    updated_at: datetime = Field(..., description="Cart last update date")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 789,
                "items": [
                    {
                        "id": 123,
                        "product_id": 456,
                        "product_name": "Premium T-Shirt",
                        "product_slug": "premium-t-shirt",
                        "product_image_url": "https://example.com/images/tshirt.jpg",
                        "quantity": 2,
                        "unit_price": "29.99",
                        "sale_price": "24.99",
                        "total_price": "49.98",
                        "is_available": True,
                        "added_at": "2025-07-29T10:30:00Z"
                    }
                ],
                "total_items": 2,
                "total_amount": "59.98",
                "total_discount": "10.00",
                "final_amount": "49.98",
                "created_at": "2025-07-29T10:00:00Z",
                "updated_at": "2025-07-29T10:30:00Z"
            }
        }


class CartSummaryResponse(BaseModel):
    """Schema for cart summary"""
    total_items: int = Field(..., ge=0, description="Total number of items")
    total_amount: Decimal = Field(..., ge=0, description="Total amount")
    items_count: int = Field(..., ge=0, description="Number of different items")

    class Config:
        json_schema_extra = {
            "example": {
                "total_items": 5,
                "total_amount": "124.95",
                "items_count": 3
            }
        }
