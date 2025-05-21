from typing import Optional

from pydantic import BaseModel


class ProductSchema(BaseModel):
    """Schema for product information in API responses"""
    product_id: int
    gender: str
    year: int
    product_display_name: str
    image_url: str


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
