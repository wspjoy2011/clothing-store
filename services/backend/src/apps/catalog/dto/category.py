from dataclasses import dataclass, field
from typing import List


@dataclass
class ArticleTypeInfoDTO:
    """DTO for article type basic information"""
    id: int
    name: str


@dataclass
class SubCategoryInfoDTO:
    """DTO for subcategory with its article types"""
    id: int
    name: str
    article_types: List[ArticleTypeInfoDTO] = field(default_factory=list)


@dataclass
class MasterCategoryInfoDTO:
    """DTO for master category with its subcategories"""
    id: int
    name: str
    sub_categories: List[SubCategoryInfoDTO] = field(default_factory=list)


@dataclass
class CategoryMenuDTO:
    """DTO for the entire category menu structure"""
    categories: List[MasterCategoryInfoDTO] = field(default_factory=list)
