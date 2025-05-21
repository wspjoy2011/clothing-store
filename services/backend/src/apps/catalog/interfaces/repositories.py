from abc import ABC, abstractmethod
from typing import Optional

from apps.catalog.dto.category import CategoryMenuDTO, MasterCategoryInfoDTO
from apps.catalog.dto.filters import FiltersDTO
from apps.catalog.dto.products import ProductDTO
from apps.catalog.interfaces.specifications import (
    PaginationSpecificationInterface,
    OrderingSpecificationInterface,
    FilterSpecificationInterface,
    SearchSpecificationInterface
)


class ProductRepositoryInterface(ABC):
    @abstractmethod
    async def get_products_with_specifications(
            self,
            pagination_spec: PaginationSpecificationInterface,
            ordering_spec: Optional[OrderingSpecificationInterface] = None,
            filter_spec: Optional[FilterSpecificationInterface] = None,
            search_spec: Optional[SearchSpecificationInterface] = None
    ) -> list[ProductDTO]:
        """
        Get products using pagination, ordering, and filtering specifications

        Args:
            pagination_spec: Specification for pagination
            ordering_spec: Optional specification for ordering results
            filter_spec: Optional specification for filtering results
            search_spec: Optional specification for search

        Returns:
            List of product DTOs
        """
        pass

    @abstractmethod
    async def get_products_count(
            self,
            filter_spec: Optional[FilterSpecificationInterface] = None,
            search_spec: Optional[SearchSpecificationInterface] = None
    ) -> int:
        """
        Get total count of products, optionally filtered and searched

        Args:
            filter_spec: Optional specification for filtering results
            search_spec: Optional specification for search

        Returns:
            Number of products in the database
        """
        pass

    @abstractmethod
    async def get_available_filters(
            self,
            search_spec: Optional[SearchSpecificationInterface] = None
    ) -> Optional[FiltersDTO]:
        """
        Get available filters and their possible values based on the actual data

        Args:
            search_spec: Optional search specification to limit filters to relevant options

        Returns:
            FiltersDTO object containing all available filters or None if catalog is empty
        """
        pass


class CategoryRepositoryInterface(ABC):
    """Interface for category repository operations"""

    @abstractmethod
    async def get_category_menu(self) -> CategoryMenuDTO:
        """
        Get the complete category menu structure with all master categories,
        subcategories and article types.

        Returns:
            CategoryMenuDTO: The complete category hierarchy
        """
        pass

    @abstractmethod
    async def get_master_category_by_id(self, master_category_id: int) -> Optional[MasterCategoryInfoDTO]:
        """
        Get a single master category with its subcategories and article types

        Args:
            master_category_id: The ID of the master category to retrieve

        Returns:
            Optional[MasterCategoryInfoDTO]: The master category with its hierarchy or None if not found
        """
        pass
