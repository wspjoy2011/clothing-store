from abc import ABC, abstractmethod
from typing import Optional

from apps.catalog.dto.catalog import CatalogDTO
from apps.catalog.dto.category import CategoryMenuDTO
from apps.catalog.dto.filters import FiltersDTO
from apps.catalog.dto.products import ProductDTO


class CatalogServiceInterface(ABC):
    """Interface for catalog service"""

    @abstractmethod
    async def get_products(
            self,
            page: int = 1,
            per_page: int = 10,
            ordering: Optional[str] = None,
            min_year: Optional[int] = None,
            max_year: Optional[int] = None,
            gender: Optional[str] = None,
            q: Optional[str] = None
    ) -> CatalogDTO:
        """
        Get paginated, sorted and filtered products

        Args:
            page: Page number (1-based)
            per_page: Number of items per page
            ordering: Ordering string (comma-separated fields with optional "-" prefix for descending)
            min_year: Minimum year filter
            max_year: Maximum year filter
            gender: Gender filter (comma-separated list)
            q: Search query string

        Returns:
            CatalogDTO with products and pagination info
        """
        pass

    @abstractmethod
    async def get_products_by_category(
            self,
            master_category_id: int,
            sub_category_id: Optional[int] = None,
            article_type_id: Optional[int] = None,
            page: int = 1,
            per_page: int = 10,
            ordering: Optional[str] = None,
            min_year: Optional[int] = None,
            max_year: Optional[int] = None,
            gender: Optional[str] = None,
            q: Optional[str] = None
    ) -> CatalogDTO:
        """
        Get products filtered by category with pagination, sorting and filtering

        Args:
            master_category_id: ID of the master category (required)
            sub_category_id: ID of the sub-category (optional)
            article_type_id: ID of the article type (optional)
            page: Page number (1-based)
            per_page: Number of items per page
            ordering: Ordering string (comma-separated fields with optional "-" prefix for descending)
            min_year: Minimum year filter
            max_year: Maximum year filter
            gender: Gender filter (comma-separated list)
            q: Search query string

        Returns:
            CatalogDTO with products and pagination info
        """
        pass

    @abstractmethod
    async def get_product_by_id(self, product_id: int) -> Optional[ProductDTO]:
        """
        Get detailed information about a single product by its ID

        Args:
            product_id: The ID of the product to retrieve

        Returns:
            ProductDTO with detailed product information if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_available_filters(self, q: Optional[str] = None) -> Optional[FiltersDTO]:
        """
        Get available filters and their possible values based on the actual data

        Args:
            q: Optional search query to limit filters to relevant options

        Returns:
            FiltersDTO object containing all available filters or None if catalog is empty
        """
        pass

    @abstractmethod
    async def get_available_filters_by_categories(
            self,
            master_category_id: int,
            sub_category_id: Optional[int] = None,
            article_type_id: Optional[int] = None
    ) -> Optional[FiltersDTO]:
        """
        Get available filters and their possible values based on products in specific categories

        Args:
            master_category_id: ID of the master category (required)
            sub_category_id: ID of the sub-category (optional)
            article_type_id: ID of the article type (optional)

        Returns:
            FiltersDTO object containing all available filters for the specified categories or None if no products found
        """
        pass

    @abstractmethod
    async def get_category_menu(self) -> Optional[CategoryMenuDTO]:
        """
        Get the complete category menu with all master categories,
        subcategories and article types.

        Returns:
            CategoryMenuDTO: The complete category hierarchy if categories is empty
        """
        pass

    @abstractmethod
    async def get_product_suggestions(self, query: str, limit: int = 10) -> list[str]:
        """
        Get product name suggestions for autocomplete

        Args:
            query: Search query string
            limit: Maximum number of suggestions to return

        Returns:
            List of product name suggestions
        """
        pass
