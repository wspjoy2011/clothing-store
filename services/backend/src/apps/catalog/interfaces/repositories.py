from abc import ABC, abstractmethod

from apps.catalog.dto.products import ProductDTO


class ProductRepositoryInterface(ABC):

    @abstractmethod
    async def get_products_with_pagination(self, offset: int, limit: int) -> list[ProductDTO]:
        pass

    @abstractmethod
    async def get_products_count(self) -> int:
        pass
