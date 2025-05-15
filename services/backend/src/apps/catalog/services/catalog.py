from typing import Optional, Callable

from apps.catalog.dto.catalog import CatalogDTO, PaginationDTO
from apps.catalog.dto.products import ProductDTO
from apps.catalog.interfaces.repositories import ProductRepositoryInterface
from apps.catalog.interfaces.services import CatalogServiceInterface
from apps.catalog.interfaces.specifications import (
    PaginationSpecificationInterface,
    OrderingSpecificationInterface,
    FilterSpecificationInterface
)

PaginationSpecificationFactory = Callable[[int, int], PaginationSpecificationInterface]
OrderingSpecificationFactory = Callable[[Optional[str], Optional[str]], OrderingSpecificationInterface]
FilterSpecificationFactory = Callable[[Optional[int], Optional[int], Optional[str]], FilterSpecificationInterface]


class CatalogService(CatalogServiceInterface):
    """Service for catalog operations"""

    def __init__(
            self,
            product_repository: ProductRepositoryInterface,
            pagination_specification_factory: PaginationSpecificationFactory,
            ordering_specification_factory: OrderingSpecificationFactory,
            filter_specification_factory: FilterSpecificationFactory,
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
        pagination_spec = self._pagination_specification_factory(page, per_page)

        ordering_spec = self._ordering_specification_factory(ordering)

        filter_spec = None
        if min_year is not None or max_year is not None or gender:
            filter_spec = self._filter_specification_factory(
                min_year=min_year,
                max_year=max_year,
                gender=gender
            )

        products = await self._product_repository.get_products_with_specifications(
            pagination_spec,
            ordering_spec,
            filter_spec
        )

        total = await self._product_repository.get_products_count(filter_spec)

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
