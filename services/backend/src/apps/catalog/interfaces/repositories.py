from abc import ABC, abstractmethod
from typing import Optional

from apps.catalog.dto.products import ProductDTO
from apps.catalog.interfaces.specifications import PaginationSpecificationInterface, OrderingSpecificationInterface


class ProductRepositoryInterface(ABC):
    @abstractmethod
    async def get_products_with_specifications(
        self,
            pagination_spec: PaginationSpecificationInterface,
            ordering_spec: Optional[OrderingSpecificationInterface] = None
    ) -> list[ProductDTO]:
        pass

    @abstractmethod
    async def get_products_count(self) -> int:
        pass
