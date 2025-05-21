from pydantic import BaseModel, Field
from typing import List


class ArticleTypeInfoDTO(BaseModel):
    """DTO for article type basic information"""
    id: int = Field(..., alias="article_type_id")
    name: str


class SubCategoryInfoDTO(BaseModel):
    """DTO for subcategory with its article types"""
    id: int = Field(..., alias="sub_category_id")
    name: str
    article_types: List[ArticleTypeInfoDTO] = []


class MasterCategoryInfoDTO(BaseModel):
    """DTO for master category with its subcategories"""
    id: int = Field(..., alias="master_category_id")
    name: str
    sub_categories: List[SubCategoryInfoDTO] = []


class CategoryMenuDTO(BaseModel):
    """DTO for the entire category menu structure"""
    categories: List[MasterCategoryInfoDTO] = []
