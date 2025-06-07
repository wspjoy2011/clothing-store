from typing import Optional, List, Any, Tuple

from apps.catalog.dto.filters import FiltersDTO, CheckboxFilterDTO, RangeFilterDTO
from apps.catalog.dto.products import ProductDTO
from apps.catalog.interfaces.repositories import ProductRepositoryInterface
from apps.catalog.interfaces.specifications import (
    PaginationSpecificationInterface,
    OrderingSpecificationInterface,
    FilterSpecificationInterface,
    SearchSpecificationInterface,
    CategorySpecificationInterface
)
from db.interfaces import DAOInterface, SQLQueryBuilderInterface
from settings.logging_config import get_logger

logger = get_logger(__name__, "app")


class ProductRepository(ProductRepositoryInterface):
    """Repository implementation for product operations using SQL database"""

    APP_NAME = "catalog"

    def __init__(self, dao: DAOInterface, query_builder: SQLQueryBuilderInterface):
        """
        Initialize product repository

        Args:
            dao: Data Access Object for database operations
            query_builder: SQL query builder for constructing queries
        """
        self._dao = dao
        self._query_builder = query_builder

    async def get_product_by_id(self, product_id: int) -> Optional[ProductDTO]:
        """
        Get a single product by its ID

        Args:
            product_id: The ID of the product to retrieve

        Returns:
            ProductDTO if found, None otherwise
        """
        query = f"""
            SELECT product_id, gender, year, product_display_name, image_url, slug
            FROM {self.APP_NAME}_products 
            WHERE product_id = %s
        """

        logger.info(f"Get product by ID query: {query}")
        logger.info(f"Get product by ID params: [{product_id}]")

        result = await self._dao.execute(query, [product_id], fetch_one=True)

        if not result:
            return None

        return ProductDTO(
            product_id=int(result[0]),
            gender=result[1],
            year=int(result[2]),
            product_display_name=result[3],
            image_url=result[4],
            slug=result[5],
        )

    async def get_products_with_specifications(
            self,
            pagination_spec: PaginationSpecificationInterface,
            ordering_spec: Optional[OrderingSpecificationInterface] = None,
            filter_spec: Optional[FilterSpecificationInterface] = None,
            search_spec: Optional[SearchSpecificationInterface] = None
    ) -> List[ProductDTO]:
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
        return await self._get_products_with_specs(
            pagination_spec=pagination_spec,
            ordering_spec=ordering_spec,
            filter_spec=filter_spec,
            search_spec=search_spec,
            log_prefix="Final"
        )

    async def get_products_with_specifications_by_categories(
            self,
            category_spec: CategorySpecificationInterface,
            pagination_spec: PaginationSpecificationInterface,
            ordering_spec: Optional[OrderingSpecificationInterface] = None,
            filter_spec: Optional[FilterSpecificationInterface] = None,
            search_spec: Optional[SearchSpecificationInterface] = None
    ) -> List[ProductDTO]:
        """
        Get products filtered by category and other specifications

        Args:
            category_spec: Specification for category filtering
            pagination_spec: Specification for pagination
            ordering_spec: Optional specification for ordering results
            filter_spec: Optional specification for filtering results
            search_spec: Optional specification for search

        Returns:
            List of product DTOs
        """
        return await self._get_products_with_specs(
            pagination_spec=pagination_spec,
            ordering_spec=ordering_spec,
            filter_spec=filter_spec,
            search_spec=search_spec,
            category_spec=category_spec,
            log_prefix="Category products"
        )

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
        return await self._get_products_count(
            filter_spec=filter_spec,
            search_spec=search_spec,
            log_prefix="Final count"
        )

    async def get_products_count_by_categories(
            self,
            category_spec: CategorySpecificationInterface,
            filter_spec: Optional[FilterSpecificationInterface] = None,
            search_spec: Optional[SearchSpecificationInterface] = None
    ) -> int:
        """
        Get count of products filtered by category and other specifications

        Args:
            category_spec: Specification for category filtering
            filter_spec: Optional specification for filtering results
            search_spec: Optional specification for search

        Returns:
            Number of products matching the criteria
        """
        return await self._get_products_count(
            filter_spec=filter_spec,
            search_spec=search_spec,
            category_spec=category_spec,
            log_prefix="Category products count"
        )

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
        if not search_spec or search_spec.is_empty():
            return await self._get_all_filters()

        return await self._get_filtered_filters(search_spec)

    async def get_available_filters_by_categories(
            self,
            category_spec: CategorySpecificationInterface,
    ) -> Optional[FiltersDTO]:
        """
        Get available filters and their possible values based on products in specific categories

        Args:
            category_spec: Specification for category filtering

        Returns:
            FiltersDTO object containing all available filters for the specified categories or None if no products found
        """
        if category_spec.is_empty():
            return await self._get_all_filters()

        return await self._get_category_filters(category_spec)

    async def _get_category_filters(self, category_spec: CategorySpecificationInterface) -> Optional[FiltersDTO]:
        """
        Get filters for specific categories

        Args:
            category_spec: Specification for category filtering

        Returns:
            FiltersDTO object with available filters for categories or None if no products found
        """
        category_sql, category_params = category_spec.to_sql()

        count_query = f"SELECT COUNT(*) FROM {self.APP_NAME}_products " + category_sql
        logger.info(f"Category filters count query: {count_query}")
        logger.info(f"Category filters count params: {category_params}")

        count_result = await self._dao.execute(count_query, category_params, fetch_one=True)

        if not count_result or count_result[0] == 0:
            return None

        gender_query = f"SELECT DISTINCT gender FROM {self.APP_NAME}_products " + category_sql
        logger.info(f"Category filters gender query: {gender_query}")
        logger.info(f"Category filters gender params: {category_params}")

        gender_result = await self._dao.execute(gender_query, category_params)
        gender_values = [row[0] for row in gender_result] if gender_result else []

        year_query = f"SELECT MIN(year), MAX(year) FROM {self.APP_NAME}_products " + category_sql + " AND year IS NOT NULL"
        logger.info(f"Category filters year query: {year_query}")
        logger.info(f"Category filters year params: {category_params}")

        year_result = await self._dao.execute(year_query, category_params, fetch_one=True)
        min_year, max_year = year_result if year_result else (None, None)

        return FiltersDTO(
            gender=CheckboxFilterDTO(values=gender_values) if gender_values else None,
            year=RangeFilterDTO(min=min_year, max=max_year) if min_year and max_year else None
        )

    async def _get_products_with_specs(
            self,
            pagination_spec: PaginationSpecificationInterface,
            ordering_spec: Optional[OrderingSpecificationInterface] = None,
            filter_spec: Optional[FilterSpecificationInterface] = None,
            search_spec: Optional[SearchSpecificationInterface] = None,
            category_spec: Optional[CategorySpecificationInterface] = None,
            log_prefix: str = "Products"
    ) -> List[ProductDTO]:
        """
        Get products with specifications applied using query builder

        Args:
            pagination_spec: Specification for pagination
            ordering_spec: Optional specification for ordering results
            filter_spec: Optional specification for filtering results
            search_spec: Optional specification for search
            category_spec: Optional specification for category filtering
            log_prefix: Prefix for logging messages

        Returns:
            List of product DTOs matching the specifications
        """
        self._prepare_query_builder(filter_spec, search_spec, ordering_spec, category_spec)
        self._query_builder.limit(pagination_spec.get_limit()).offset(pagination_spec.get_offset())

        query, params = self._query_builder.build()
        logger.info(f"{log_prefix} query: {query}")
        logger.info(f"{log_prefix} params: {params}")

        result = await self._dao.execute(query, params)

        return [
            ProductDTO(
                product_id=int(row[0]),
                gender=row[1],
                year=int(row[2]),
                product_display_name=row[3],
                image_url=row[4],
                slug=row[5],
            )
            for row in (result or [])
        ]

    async def _get_products_count(
            self,
            filter_spec: Optional[FilterSpecificationInterface] = None,
            search_spec: Optional[SearchSpecificationInterface] = None,
            category_spec: Optional[CategorySpecificationInterface] = None,
            log_prefix: str = "Count"
    ) -> int:
        """
        Get count of products matching specifications

        Args:
            filter_spec: Optional specification for filtering results
            search_spec: Optional specification for search
            category_spec: Optional specification for category filtering
            log_prefix: Prefix for logging messages

        Returns:
            Number of products matching the criteria
        """
        self._query_builder.reset().select("COUNT(*)")

        if category_spec and not category_spec.is_empty():
            self._apply_category_spec(category_spec)

        if filter_spec and not filter_spec.is_empty():
            filter_sql, filter_params = filter_spec.to_sql()
            self._parse_sql_conditions(filter_sql, filter_params)

        if search_spec and not search_spec.is_empty():
            search_sql, search_params = search_spec.to_sql()
            where_sql, _ = self._split_search_sql(search_sql)
            self._parse_sql_conditions(where_sql, search_params[:1])

        query, params = self._query_builder.build()

        logger.info(f"{log_prefix} query: {query}")
        logger.info(f"{log_prefix} params: {params}")

        result = await self._dao.execute(query, params, fetch_one=True)
        return result[0] if result else 0

    async def _get_all_filters(self) -> Optional[FiltersDTO]:
        """
        Get all available filters from the entire product catalog

        Returns:
            FiltersDTO object containing all available filters or None if catalog is empty
        """
        count_query = f"SELECT COUNT(*) FROM {self.APP_NAME}_products"
        logger.info(f"Filters count query: {count_query}")

        count_result = await self._dao.execute(count_query, [], fetch_one=True)

        if not count_result or count_result[0] == 0:
            return None

        gender_query = f"SELECT DISTINCT gender FROM {self.APP_NAME}_products"
        logger.info(f"Filters gender query: {gender_query}")

        gender_result = await self._dao.execute(gender_query, [])
        gender_values = [row[0] for row in gender_result] if gender_result else []

        year_query = f"SELECT MIN(year), MAX(year) FROM {self.APP_NAME}_products WHERE year IS NOT NULL"
        logger.info(f"Filters year query: {year_query}")

        year_result = await self._dao.execute(year_query, [], fetch_one=True)
        min_year, max_year = year_result if year_result else (None, None)

        return FiltersDTO(
            gender=CheckboxFilterDTO(values=gender_values) if gender_values else None,
            year=RangeFilterDTO(min=min_year, max=max_year) if min_year and max_year else None
        )

    async def _get_filtered_filters(self, search_spec: SearchSpecificationInterface) -> Optional[FiltersDTO]:
        """
        Get available filters based on search results

        Args:
            search_spec: Search specification to filter available options

        Returns:
            FiltersDTO object with available filters for search results or None if no results
        """
        self._query_builder.reset()

        search_sql, search_params = search_spec.to_sql()
        where_sql, _ = self._split_search_sql(search_sql)
        self._parse_sql_conditions(where_sql, search_params[:1])

        count_query, count_params = self._query_builder.build_count()
        logger.info(f"Filtered filters count query: {count_query}")
        logger.info(f"Filtered filters count params: {count_params}")

        count_result = await self._dao.execute(count_query, count_params, fetch_one=True)

        if not count_result or count_result[0] == 0:
            return None

        gender_values = await self._get_filtered_gender_values(where_sql, search_params)

        min_year, max_year = await self._get_filtered_year_range(where_sql, search_params)

        return FiltersDTO(
            gender=CheckboxFilterDTO(values=gender_values) if gender_values else None,
            year=RangeFilterDTO(min=min_year, max=max_year) if min_year and max_year else None
        )

    async def _get_filtered_gender_values(self, where_sql: str, search_params: List[Any]) -> List[str]:
        """
        Get available gender values for filtered search results

        Args:
            where_sql: WHERE clause SQL for filtering
            search_params: Parameters for the WHERE clause

        Returns:
            List of available gender values
        """
        self._query_builder.reset().select("DISTINCT gender")
        self._parse_sql_conditions(where_sql, search_params[:1])
        self._query_builder.where("gender IS NOT NULL")

        gender_query, gender_params = self._query_builder.build()
        logger.info(f"Filtered filters gender query: {gender_query}")
        logger.info(f"Filtered filters gender params: {gender_params}")

        gender_result = await self._dao.execute(gender_query, gender_params)
        return [row[0] for row in gender_result] if gender_result else []

    async def _get_filtered_year_range(
            self,
            where_sql: str,
            search_params: List[Any]
    ) -> Tuple[Optional[int], Optional[int]]:
        """
        Get available year range for filtered search results

        Args:
            where_sql: WHERE clause SQL for filtering
            search_params: Parameters for the WHERE clause

        Returns:
            Tuple of (min_year, max_year) or (None, None) if no results
        """
        self._query_builder.reset().select("MIN(year)", "MAX(year)")
        self._parse_sql_conditions(where_sql, search_params[:1])
        self._query_builder.where("year IS NOT NULL")

        year_query, year_params = self._query_builder.build()
        logger.info(f"Filtered filters year query: {year_query}")
        logger.info(f"Filtered filters year params: {year_params}")

        year_result = await self._dao.execute(year_query, year_params, fetch_one=True)
        return year_result if year_result else (None, None)

    def _prepare_query_builder(
            self,
            filter_spec: Optional[FilterSpecificationInterface],
            search_spec: Optional[SearchSpecificationInterface],
            ordering_spec: Optional[OrderingSpecificationInterface] = None,
            category_spec: Optional[CategorySpecificationInterface] = None
    ) -> None:
        """
        Prepare query builder with all specifications

        Args:
            filter_spec: Optional specification for filtering results
            search_spec: Optional specification for search
            ordering_spec: Optional specification for ordering results
            category_spec: Optional specification for category filtering
        """
        self._query_builder.reset().select(
            "product_id", "gender", "year", "product_display_name", "image_url", "slug"
        )

        if category_spec and not category_spec.is_empty():
            self._apply_category_spec(category_spec)

        if filter_spec and not filter_spec.is_empty():
            filter_sql, filter_params = filter_spec.to_sql()
            self._parse_sql_conditions(filter_sql, filter_params)

        order_by_clauses = []
        order_by_params = []

        if search_spec and not search_spec.is_empty():
            search_sql, search_params = search_spec.to_sql()
            where_sql, search_order_sql = self._split_search_sql(search_sql)
            self._parse_sql_conditions(where_sql, search_params[:1])

            if search_order_sql:
                order_by_clauses.append(search_order_sql)
                order_by_params.append(search_params[1])

        if ordering_spec:
            ordering_sql, _ = ordering_spec.to_sql()
            ordering_sql_cleaned = ordering_sql.replace("ORDER BY", "").strip()
            if ordering_sql_cleaned:
                order_by_clauses.append(ordering_sql_cleaned)

        if order_by_clauses:
            final_ordering = ", ".join(order_by_clauses)
            self._query_builder.order_by(final_ordering, *order_by_params)

    def _apply_category_spec(self, category_spec: CategorySpecificationInterface) -> None:
        """
        Apply category specification to query builder

        Args:
            category_spec: Category specification with joins and filters
        """
        category_sql, category_params = category_spec.to_sql()
        joins_part, where_part = category_sql.split("WHERE", 1)

        for join_clause in joins_part.strip().split("JOIN"):
            if join_clause.strip():
                self._query_builder.join(f"JOIN {join_clause.strip()}")

        self._query_builder.where(where_part.strip(), *category_params)

    def _parse_sql_conditions(self, sql_conditions: str, params: List[Any]) -> None:
        """
        Parse and apply SQL conditions to query builder

        Args:
            sql_conditions: SQL conditions string (may include WHERE keyword)
            params: Parameters for the SQL conditions
        """
        if sql_conditions.startswith("WHERE"):
            conditions_text = sql_conditions.replace("WHERE", "").strip()
            self._query_builder.where(conditions_text, *params)

    @staticmethod
    def _split_search_sql(search_sql: str) -> Tuple[str, str]:
        """
        Split search SQL into WHERE and ORDER BY parts

        Args:
            search_sql: Complete search SQL string

        Returns:
            Tuple of (where_part, order_by_part)
        """
        if "ORDER BY" in search_sql:
            where_part, order_by_part = search_sql.split("ORDER BY", 1)
            return where_part.strip(), order_by_part.strip()
        return search_sql.strip(), ""
