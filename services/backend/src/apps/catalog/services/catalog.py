from typing import Optional, Callable

from apps.catalog.dto.catalog import CatalogDTO, PaginationDTO
from apps.catalog.dto.filters import FiltersDTO
from apps.catalog.interfaces.repositories import ProductRepositoryInterface
from apps.catalog.interfaces.services import CatalogServiceInterface
from apps.catalog.interfaces.specifications import (
    PaginationSpecificationInterface,
    OrderingSpecificationInterface,
    FilterSpecificationInterface,
    SearchSpecificationInterface
)

PaginationSpecificationFactory = Callable[[int, int], PaginationSpecificationInterface]
OrderingSpecificationFactory = Callable[[Optional[str]], OrderingSpecificationInterface]
FilterSpecificationFactory = Callable[[Optional[int], Optional[int], Optional[str]], FilterSpecificationInterface]
SearchSpecificationFactory = Callable[[Optional[str]], SearchSpecificationInterface]


class CatalogService(CatalogServiceInterface):
    """Service for catalog operations"""

    def __init__(
            self,
            product_repository: ProductRepositoryInterface,
            pagination_specification_factory: PaginationSpecificationFactory,
            ordering_specification_factory: OrderingSpecificationFactory,
            filter_specification_factory: FilterSpecificationFactory,
            search_specification_factory: SearchSpecificationFactory
    ):
        """
        Initialize catalog service

        Args:
            product_repository: Repository for product data access
            pagination_specification_factory: Factory for creating pagination specifications
            ordering_specification_factory: Factory for creating ordering specifications
            filter_specification_factory: Factory for creating filter specifications
        """
        self._product_repository = product_repository
        self._pagination_specification_factory = pagination_specification_factory
        self._ordering_specification_factory = ordering_specification_factory
        self._filter_specification_factory = filter_specification_factory
        self._search_specification_factory = search_specification_factory

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
        pagination_spec = self._pagination_specification_factory(page, per_page)

        ordering_spec = self._ordering_specification_factory(ordering)

        filter_spec = None
        if min_year is not None or max_year is not None or gender:
            filter_spec = self._filter_specification_factory(min_year, max_year, gender)

        search_spec = None
        if q:
            search_spec = self._search_specification_factory(q)

        products = await self._product_repository.get_products_with_specifications(
            pagination_spec,
            ordering_spec,
            filter_spec,
            search_spec
        )

        total = await self._product_repository.get_products_count(filter_spec, search_spec)

        total_pages = (total + per_page - 1) // per_page if per_page > 0 else 0

        return CatalogDTO(
            products=products,
            pagination=PaginationDTO(
                page=page,
                per_page=per_page,
                total_items=total,
                total_pages=total_pages
            )
        )

    async def get_available_filters(self) -> Optional[FiltersDTO]:
        """
        Get available filters and their possible values based on the actual data

        Returns:
            FiltersDTO object containing all available filters or None if catalog is empty
        """
        return await self._product_repository.get_available_filters()
