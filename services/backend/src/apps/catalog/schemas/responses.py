from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class InventorySchema(BaseModel):
    """Schema for product inventory information in API responses"""
    id: int
    product_id: int
    base_price: Decimal
    sale_price: Optional[Decimal] = None
    currency: str
    available_quantity: int
    is_active: bool
    is_in_stock: bool
    created_at: datetime
    updated_at: datetime


class ProductSchema(BaseModel):
    """Schema for product information in API responses

    Year, display name and image are nullable in the catalogue table, so a
    product missing any of them is served as it is rather than failing the page.
    """
    product_id: int
    gender: str
    year: Optional[int] = None
    product_display_name: Optional[str] = None
    image_url: Optional[str] = None
    slug: str
    inventory: Optional[InventorySchema] = None


class ProductListResponseSchema(BaseModel):
    """Schema for paginated product list response with navigation links"""
    products: list[ProductSchema]
    prev_page: Optional[str] = None
    next_page: Optional[str] = None
    total_pages: int
    total_items: int


class ArticleTypeSchema(BaseModel):
    """Schema for article type information in API responses"""
    id: int
    name: str


class SubCategorySchema(BaseModel):
    """Schema for subcategory information with article types in API responses"""
    id: int
    name: str
    article_types: list[ArticleTypeSchema] = []


class MasterCategorySchema(BaseModel):
    """Schema for master category information with subcategories in API responses"""
    id: int
    name: str
    sub_categories: list[SubCategorySchema] = []


class CategoryMenuResponseSchema(BaseModel):
    """Schema for category menu response with all hierarchy levels"""
    categories: list[MasterCategorySchema] = []
