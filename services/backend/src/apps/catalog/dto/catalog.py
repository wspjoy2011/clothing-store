from dataclasses import dataclass
from typing import List

from apps.catalog.dto.products import ProductDTO


@dataclass
class PaginationDTO:
    """Data transfer object for pagination information"""
    page: int
    per_page: int
    total_items: int
    total_pages: int


@dataclass
class CatalogDTO:
    """Data transfer object for catalog data with pagination"""
    products: List[ProductDTO]
    pagination: PaginationDTO
