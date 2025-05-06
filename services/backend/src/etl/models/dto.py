from typing import List, Optional

from pydantic import BaseModel


class MasterCategoryDTO(BaseModel):
    name: str


class SubCategoryDTO(BaseModel):
    master_category: str
    name: str


class ArticleTypeDTO(BaseModel):
    sub_category: str
    name: str


class BaseColourDTO(BaseModel):
    name: str


class SeasonDTO(BaseModel):
    name: str


class UsageTypeDTO(BaseModel):
    name: str


class ProductDTO(BaseModel):
    product_id: int
    gender: str
    year: Optional[int] = None
    product_display_name: Optional[str] = None
    article_type: str
    base_colour: Optional[str] = None
    season: Optional[str] = None
    usage: Optional[str] = None


class ImageDTO(BaseModel):
    product_id: int
    image_url: str


class ETLResultDTO(BaseModel):
    master_categories: List[MasterCategoryDTO]
    sub_categories: List[SubCategoryDTO]
    article_types: List[ArticleTypeDTO]
    base_colours: List[BaseColourDTO]
    seasons: List[SeasonDTO]
    usage_types: List[UsageTypeDTO]
    products: List[ProductDTO]
    images: List[ImageDTO]
