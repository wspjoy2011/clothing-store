from abc import ABC, abstractmethod
from typing import Optional

from apps.catalog.dto.products import ProductDTO


class CatalogServiceInterface(ABC):

    @abstractmethod
    async def get_paginated_products(self, page: int, per_page: int) -> Optional[list[ProductDTO]]:
        pass

    @abstractmethod
    async def get_products_count(self) -> int:
        pass
