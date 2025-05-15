from abc import ABC, abstractmethod
from typing import Optional

from apps.catalog.dto.products import ProductDTO
from apps.catalog.interfaces.specifications import (
    PaginationSpecificationInterface,
    OrderingSpecificationInterface,
    FilterSpecificationInterface
)


class ProductRepositoryInterface(ABC):
    @abstractmethod
    async def get_products_with_specifications(
            self,
            pagination_spec: PaginationSpecificationInterface,
            ordering_spec: Optional[OrderingSpecificationInterface] = None,
            filter_spec: Optional[FilterSpecificationInterface] = None
    ) -> list[ProductDTO]:
        """
        Get products using pagination, ordering, and filtering specifications

        Args:
            pagination_spec: Specification for pagination
            ordering_spec: Optional specification for ordering results
            filter_spec: Optional specification for filtering results

        Returns:
            List of product DTOs
        """
        pass

    @abstractmethod
    async def get_products_count(
            self,
            filter_spec: Optional[FilterSpecificationInterface] = None
    ) -> int:
        """
        Get total count of products, optionally filtered

        Args:
            filter_spec: Optional specification for filtering results

        Returns:
            Number of products in the database
        """
        pass
