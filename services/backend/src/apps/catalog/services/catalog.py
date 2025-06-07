from typing import Optional, Callable

from apps.catalog.dto.catalog import CatalogDTO, PaginationDTO
from apps.catalog.dto.category import CategoryMenuDTO
from apps.catalog.dto.filters import FiltersDTO
from apps.catalog.dto.products import ProductDTO
from apps.catalog.interfaces.repositories import (
    ProductRepositoryInterface,
    CategoryRepositoryInterface
)
from apps.catalog.interfaces.services import CatalogServiceInterface
from apps.catalog.interfaces.specifications import (
    PaginationSpecificationInterface,
    OrderingSpecificationInterface,
    FilterSpecificationInterface,
    SearchSpecificationInterface,
    CategorySpecificationInterface
)
from search.interfaces import AutocompleteClientInterface

PaginationSpecificationFactory = Callable[[int, int], PaginationSpecificationInterface]
OrderingSpecificationFactory = Callable[[Optional[str]], OrderingSpecificationInterface]
FilterSpecificationFactory = Callable[[Optional[int], Optional[int], Optional[str]], FilterSpecificationInterface]
SearchSpecificationFactory = Callable[[Optional[str]], SearchSpecificationInterface]
CategorySpecificationFactory = Callable[[int, Optional[int], Optional[int]], CategorySpecificationInterface]


class CatalogService(CatalogServiceInterface):
    """Service for catalog operations"""

    def __init__(
            self,
            product_repository: ProductRepositoryInterface,
            category_repository: CategoryRepositoryInterface,
            pagination_specification_factory: PaginationSpecificationFactory,
            ordering_specification_factory: OrderingSpecificationFactory,
            filter_specification_factory: FilterSpecificationFactory,
            search_specification_factory: SearchSpecificationFactory,
            category_specification_factory: CategorySpecificationFactory,
            autocomplete_client: AutocompleteClientInterface
    ):
        """
        Initialize catalog service

        Args:
            product_repository: Repository for product data access
            category_repository: Repository for category data access
            pagination_specification_factory: Factory for creating pagination specifications
            ordering_specification_factory: Factory for creating ordering specifications
            filter_specification_factory: Factory for creating filter specifications
            search_specification_factory: Factory for creating search specifications
            category_specification_factory: Factory for creating category specifications
            autocomplete_client: Client for autocomplete operations
        """
        self._product_repository = product_repository
        self._category_repository = category_repository
        self._pagination_specification_factory = pagination_specification_factory
        self._ordering_specification_factory = ordering_specification_factory
        self._filter_specification_factory = filter_specification_factory
        self._search_specification_factory = search_specification_factory
        self._category_specification_factory = category_specification_factory
        self._autocomplete_client = autocomplete_client

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
        category_spec = self._category_specification_factory(
            master_category_id, sub_category_id, article_type_id
        )

        pagination_spec = self._pagination_specification_factory(page, per_page)

        ordering_spec = self._ordering_specification_factory(ordering)

        filter_spec = None
        if min_year is not None or max_year is not None or gender:
            filter_spec = self._filter_specification_factory(min_year, max_year, gender)

        search_spec = None
        if q:
            search_spec = self._search_specification_factory(q)

        products = await self._product_repository.get_products_with_specifications_by_categories(
            category_spec,
            pagination_spec,
            ordering_spec,
            filter_spec,
            search_spec
        )

        total = await self._product_repository.get_products_count_by_categories(
            category_spec,
            filter_spec,
            search_spec
        )

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

    async def get_product_by_id(self, product_id: int) -> Optional[ProductDTO]:
        """
        Get detailed information about a single product by its ID

        Args:
            product_id: The ID of the product to retrieve

        Returns:
            ProductDTO with detailed product information if found, None otherwise
        """
        return await self._product_repository.get_product_by_id(product_id)

    async def get_product_by_slug(self, slug: str) -> Optional[ProductDTO]:
        """
        Get detailed information about a single product by its slug

        Args:
            slug: The slug of the product to retrieve

        Returns:
            ProductDTO with detailed product information if found, None otherwise
        """
        return await self._product_repository.get_product_by_slug(slug)

    async def get_available_filters(self, q: Optional[str] = None) -> Optional[FiltersDTO]:
        """
        Get available filters and their possible values based on the actual data

        Args:
            q: Optional search query to limit filters to relevant options

        Returns:
            FiltersDTO object containing all available filters or None if catalog is empty
        """
        search_spec = None
        if q:
            search_spec = self._search_specification_factory(q)

        return await self._product_repository.get_available_filters(search_spec)

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
        category_spec = self._category_specification_factory(
            master_category_id, sub_category_id, article_type_id
        )

        return await self._product_repository.get_available_filters_by_categories(category_spec)

    async def get_category_menu(self) -> Optional[CategoryMenuDTO]:
        """
        Get the complete category menu with all master categories,
        subcategories and article types.

        Returns:
            CategoryMenuDTO: The complete category hierarchy if categories is empty
        """
        return await self._category_repository.get_category_menu()

    async def get_product_suggestions(self, query: str, limit: int = 10) -> list[str]:
        """
        Get product name suggestions for autocomplete

        Args:
            query: Search query string
            limit: Maximum number of suggestions to return

        Returns:
            List of product name suggestions
        """
        return await self._autocomplete_client.get_suggestions(query, limit)
