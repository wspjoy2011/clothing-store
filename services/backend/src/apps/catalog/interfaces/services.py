from abc import ABC, abstractmethod
from typing import Optional

from apps.catalog.dto.catalog import CatalogDTO
from apps.catalog.dto.filters import FiltersDTO


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
            gender: Optional[str] = None
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

        Returns:
            CatalogDTO with products and pagination info
        """
        pass

    @abstractmethod
    async def get_available_filters(self) -> Optional[FiltersDTO]:
        """
        Get available filters and their possible values based on the actual data

        Returns:
            FiltersDTO object containing all available filters or None if catalog is empty
        """
        pass
