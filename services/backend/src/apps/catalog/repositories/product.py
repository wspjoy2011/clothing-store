import re
from typing import Optional, List, Any, Tuple
from decimal import Decimal

from apps.catalog.dto.filters import FiltersDTO, CheckboxFilterDTO, RangeFilterDTO, AvailabilityFilterDTO, \
    PriceRangeFilterDTO
from apps.catalog.dto.products import ProductDTO, InventoryDTO
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
            SELECT 
                p.product_id, p.gender, p.year, p.product_display_name, p.image_url, p.slug,
                i.id, i.base_price, i.sale_price, i.currency, i.stock_quantity, 
                i.reserved_quantity, i.available_quantity, i.is_active, i.is_in_stock,
                i.created_at, i.updated_at
            FROM {self.APP_NAME}_products p
            LEFT JOIN {self.APP_NAME}_product_inventory i ON p.product_id = i.product_id
            WHERE p.product_id = %s
        """

        logger.info(f"Get product by ID query: {query}")
        logger.info(f"Get product by ID params: [{product_id}]")

        result = await self._dao.execute(query, [product_id], fetch_one=True)

        if not result:
            return None

        if isinstance(result, (list, tuple)):
            return self._build_product_dto_from_row(tuple(result))
        else:
            logger.error(f"Unexpected result type: {type(result)}")
            return None

    async def get_product_by_slug(self, slug: str) -> Optional[ProductDTO]:
        """
        Get a single product by its slug

        Args:
            slug: The slug of the product to retrieve

        Returns:
            ProductDTO if found, None otherwise
        """
        query = f"""
            SELECT 
                p.product_id, p.gender, p.year, p.product_display_name, p.image_url, p.slug,
                i.id, i.base_price, i.sale_price, i.currency, i.stock_quantity, 
                i.reserved_quantity, i.available_quantity, i.is_active, i.is_in_stock,
                i.created_at, i.updated_at
            FROM {self.APP_NAME}_products p
            LEFT JOIN {self.APP_NAME}_product_inventory i ON p.product_id = i.product_id
            WHERE p.slug = %s
        """

        logger.info(f"Get product by slug query: {query}")
        logger.info(f"Get product by slug params: [{slug}]")

        result = await self._dao.execute(query, [slug], fetch_one=True)

        if not result:
            return None

        if isinstance(result, (list, tuple)):
            return self._build_product_dto_from_row(tuple(result))
        else:
            logger.error(f"Unexpected result type: {type(result)}")
            return None

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

        count_query = f"""
            SELECT COUNT(*) FROM {self.APP_NAME}_products p
            LEFT JOIN {self.APP_NAME}_product_inventory i ON p.product_id = i.product_id
            {category_sql.replace(f'{self.APP_NAME}_products', 'p')}
        """
        logger.info(f"Category filters count query: {count_query}")
        logger.info(f"Category filters count params: {category_params}")

        count_result = await self._dao.execute(count_query, category_params, fetch_one=True)

        if not count_result or count_result[0] == 0:
            return None

        gender_query = f"""
            SELECT DISTINCT p.gender FROM {self.APP_NAME}_products p
            LEFT JOIN {self.APP_NAME}_product_inventory i ON p.product_id = i.product_id
            {category_sql.replace(f'{self.APP_NAME}_products', 'p')}
        """
        logger.info(f"Category filters gender query: {gender_query}")
        logger.info(f"Category filters gender params: {category_params}")

        gender_result = await self._dao.execute(gender_query, category_params)
        gender_values = [row[0] for row in gender_result] if gender_result else []

        year_query = f"""
            SELECT MIN(p.year), MAX(p.year) FROM {self.APP_NAME}_products p
            LEFT JOIN {self.APP_NAME}_product_inventory i ON p.product_id = i.product_id
            {category_sql.replace(f'{self.APP_NAME}_products', 'p')} AND p.year IS NOT NULL
        """
        logger.info(f"Category filters year query: {year_query}")
        logger.info(f"Category filters year params: {category_params}")

        year_result = await self._dao.execute(year_query, category_params, fetch_one=True)
        min_year, max_year = year_result if year_result else (None, None)

        price_query = f"""
            SELECT 
                MIN(COALESCE(i.sale_price, i.base_price)), 
                MAX(COALESCE(i.sale_price, i.base_price))
            FROM {self.APP_NAME}_products p
            LEFT JOIN {self.APP_NAME}_product_inventory i ON p.product_id = i.product_id
            {category_sql.replace(f'{self.APP_NAME}_products', 'p')} 
            AND i.id IS NOT NULL
        """
        logger.info(f"Category filters price query: {price_query}")
        logger.info(f"Category filters price params: {category_params}")

        price_result = await self._dao.execute(price_query, category_params, fetch_one=True)
        min_price, max_price = price_result if price_result else (None, None)

        return FiltersDTO(
            gender=CheckboxFilterDTO(values=gender_values) if gender_values else None,
            year=RangeFilterDTO(min=min_year, max=max_year) if min_year and max_year else None,
            price=PriceRangeFilterDTO(min=float(min_price), max=float(max_price)) if min_price and max_price else None,
            is_available=AvailabilityFilterDTO()
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
        self._prepare_query_builder_with_inventory(filter_spec, search_spec, ordering_spec, category_spec)
        self._query_builder.limit(pagination_spec.get_limit()).offset(pagination_spec.get_offset())

        query, params = self._query_builder.build()
        logger.info(f"{log_prefix} query: {query}")
        logger.info(f"{log_prefix} params: {params}")

        result = await self._dao.execute(query, params)

        if not result:
            return []

        return [self._build_product_dto_from_row(tuple(row)) for row in result]

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
        self._query_builder.reset().select("COUNT(*)").from_table(f"{self.APP_NAME}_products p").join(
            f"LEFT JOIN {self.APP_NAME}_product_inventory i ON p.product_id = i.product_id"
        )

        if category_spec and not category_spec.is_empty():
            self._apply_category_spec_with_alias(category_spec)

        if filter_spec and not filter_spec.is_empty():
            filter_sql, filter_params = filter_spec.to_sql()
            filter_sql = self._prefix_columns_with_alias(filter_sql, 'p')
            self._parse_sql_conditions(filter_sql, filter_params)

        if search_spec and not search_spec.is_empty():
            search_sql, search_params = search_spec.to_sql()
            where_sql, _ = self._split_search_sql(search_sql)
            where_sql = self._safe_alias_replace(where_sql, "product_display_name", "p")
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

        price_query = f"""
            SELECT 
                MIN(COALESCE(i.sale_price, i.base_price)), 
                MAX(COALESCE(i.sale_price, i.base_price))
            FROM {self.APP_NAME}_products p
            LEFT JOIN {self.APP_NAME}_product_inventory i ON p.product_id = i.product_id
            WHERE i.id IS NOT NULL
        """
        logger.info(f"Filters price query: {price_query}")

        price_result = await self._dao.execute(price_query, [], fetch_one=True)
        min_price, max_price = price_result if price_result else (None, None)

        return FiltersDTO(
            gender=CheckboxFilterDTO(values=gender_values) if gender_values else None,
            year=RangeFilterDTO(min=min_year, max=max_year) if min_year and max_year else None,
            price=PriceRangeFilterDTO(min=float(min_price), max=float(max_price)) if min_price and max_price else None,
            is_available=AvailabilityFilterDTO()
        )

    async def _get_filtered_filters(self, search_spec: SearchSpecificationInterface) -> Optional[FiltersDTO]:
        """
        Get available filters based on search results

        Args:
            search_spec: Search specification to filter available options

        Returns:
            FiltersDTO object with available filters for search results or None if no results
        """
        self._query_builder.reset().from_table(f"{self.APP_NAME}_products p").join(
            f"LEFT JOIN {self.APP_NAME}_product_inventory i ON p.product_id = i.product_id"
        )

        search_sql, search_params = search_spec.to_sql()
        where_sql, _ = self._split_search_sql(search_sql)
        where_sql = self._safe_alias_replace(where_sql, "product_display_name", "p")
        self._parse_sql_conditions(where_sql, search_params[:1])

        count_query, count_params = self._query_builder.build_count()
        logger.info(f"Filtered filters count query: {count_query}")
        logger.info(f"Filtered filters count params: {count_params}")

        count_result = await self._dao.execute(count_query, count_params, fetch_one=True)

        if not count_result or count_result[0] == 0:
            return None

        gender_values = await self._get_filtered_gender_values(where_sql, search_params)
        min_year, max_year = await self._get_filtered_year_range(where_sql, search_params)
        min_price, max_price = await self._get_filtered_price_range(where_sql, search_params)

        return FiltersDTO(
            gender=CheckboxFilterDTO(values=gender_values) if gender_values else None,
            year=RangeFilterDTO(min=min_year, max=max_year) if min_year and max_year else None,
            price=PriceRangeFilterDTO(min=min_price, max=max_price) if min_price and max_price else None,
            is_available=AvailabilityFilterDTO()
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
        self._query_builder.reset().select("DISTINCT p.gender").from_table(f"{self.APP_NAME}_products p").join(
            f"LEFT JOIN {self.APP_NAME}_product_inventory i ON p.product_id = i.product_id"
        )

        where_sql = self._safe_alias_replace(where_sql, "product_display_name", "p")
        self._parse_sql_conditions(where_sql, search_params[:1])
        self._query_builder.where("p.gender IS NOT NULL")

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
        self._query_builder.reset().select("MIN(p.year)", "MAX(p.year)").from_table(f"{self.APP_NAME}_products p").join(
            f"LEFT JOIN {self.APP_NAME}_product_inventory i ON p.product_id = i.product_id"
        )

        where_sql = self._safe_alias_replace(where_sql, "product_display_name", "p")
        self._parse_sql_conditions(where_sql, search_params[:1])
        self._query_builder.where("p.year IS NOT NULL")

        year_query, year_params = self._query_builder.build()
        logger.info(f"Filtered filters year query: {year_query}")
        logger.info(f"Filtered filters year params: {year_params}")

        year_result = await self._dao.execute(year_query, year_params, fetch_one=True)
        return year_result if year_result else (None, None)

    async def _get_filtered_price_range(
            self,
            where_sql: str,
            search_params: List[Any]
    ) -> Tuple[Optional[float], Optional[float]]:
        """
        Get available price range for filtered search results

        Args:
            where_sql: WHERE clause SQL for filtering
            search_params: Parameters for the WHERE clause

        Returns:
            Tuple of (min_price, max_price) or (None, None) if no results
        """
        self._query_builder.reset().select(
            "MIN(COALESCE(i.sale_price, i.base_price))",
            "MAX(COALESCE(i.sale_price, i.base_price))"
        ).from_table(f"{self.APP_NAME}_products p").join(
            f"LEFT JOIN {self.APP_NAME}_product_inventory i ON p.product_id = i.product_id"
        )

        where_sql = self._safe_alias_replace(where_sql, "product_display_name", "p")
        self._parse_sql_conditions(where_sql, search_params[:1])
        self._query_builder.where("i.id IS NOT NULL")

        price_query, price_params = self._query_builder.build()
        logger.info(f"Filtered filters price query: {price_query}")
        logger.info(f"Filtered filters price params: {price_params}")

        price_result = await self._dao.execute(price_query, price_params, fetch_one=True)
        if price_result and price_result[0] is not None and price_result[1] is not None:
            return float(price_result[0]), float(price_result[1])
        return None, None

    def _prepare_query_builder_with_inventory(
            self,
            filter_spec: Optional[FilterSpecificationInterface],
            search_spec: Optional[SearchSpecificationInterface],
            ordering_spec: Optional[OrderingSpecificationInterface] = None,
            category_spec: Optional[CategorySpecificationInterface] = None
    ) -> None:
        """
        Prepare query builder with all specifications including inventory join

        Args:
            filter_spec: Optional specification for filtering results
            search_spec: Optional specification for search
            ordering_spec: Optional specification for ordering results
            category_spec: Optional specification for category filtering
        """
        self._query_builder.reset().select(
            "p.product_id", "p.gender", "p.year", "p.product_display_name", "p.image_url", "p.slug",
            "i.id", "i.base_price", "i.sale_price", "i.currency", "i.stock_quantity",
            "i.reserved_quantity", "i.available_quantity", "i.is_active", "i.is_in_stock",
            "i.created_at", "i.updated_at"
        ).from_table(f"{self.APP_NAME}_products p").join(
            f"LEFT JOIN {self.APP_NAME}_product_inventory i ON p.product_id = i.product_id"
        )

        if category_spec and not category_spec.is_empty():
            self._apply_category_spec_with_alias(category_spec)

        if filter_spec and not filter_spec.is_empty():
            filter_sql, filter_params = filter_spec.to_sql()
            filter_sql = self._prefix_columns_with_alias(filter_sql, 'p')
            self._parse_sql_conditions(filter_sql, filter_params)

        order_by_clauses = []
        order_by_params = []

        if search_spec and not search_spec.is_empty():
            search_sql, search_params = search_spec.to_sql()
            where_sql, search_order_sql = self._split_search_sql(search_sql)

            where_sql = self._safe_alias_replace(where_sql, "product_display_name", "p")
            search_order_sql = self._safe_alias_replace(search_order_sql, "product_display_name", "p")

            self._parse_sql_conditions(where_sql, search_params[:1])

            if search_order_sql:
                order_by_clauses.append(search_order_sql)
                order_by_params.append(search_params[1])

        if ordering_spec:
            ordering_sql, _ = ordering_spec.to_sql()
            ordering_sql_cleaned = ordering_sql.replace("ORDER BY", "").strip()
            if ordering_sql_cleaned:
                ordering_sql_cleaned = self._prefix_ordering_fields(ordering_sql_cleaned)
                order_by_clauses.append(ordering_sql_cleaned)

        if order_by_clauses:
            final_ordering = ", ".join(order_by_clauses)
            self._query_builder.order_by(final_ordering, *order_by_params)

    def _prepare_query_builder(
            self,
            filter_spec: Optional[FilterSpecificationInterface],
            search_spec: Optional[SearchSpecificationInterface],
            ordering_spec: Optional[OrderingSpecificationInterface] = None,
            category_spec: Optional[CategorySpecificationInterface] = None
    ) -> None:
        """
        Prepare query builder with all specifications (legacy method for backward compatibility)

        Args:
            filter_spec: Optional specification for filtering results
            search_spec: Optional specification for search
            ordering_spec: Optional specification for ordering results
            category_spec: Optional specification for category filtering
        """
        self._prepare_query_builder_with_inventory(filter_spec, search_spec, ordering_spec, category_spec)

    def _apply_category_spec_with_alias(self, category_spec: CategorySpecificationInterface) -> None:
        """
        Apply category specification to query builder with proper table aliases

        Args:
            category_spec: Category specification with joins and filters
        """
        category_sql, category_params = category_spec.to_sql()
        joins_part, where_part = category_sql.split("WHERE", 1)

        joins_part = joins_part.replace(f"{self.APP_NAME}_products.article_type_id", "p.article_type_id")

        for join_clause in joins_part.strip().split("JOIN"):
            if join_clause.strip():
                self._query_builder.join(f"JOIN {join_clause.strip()}")

        self._query_builder.where(where_part.strip(), *category_params)

    def _apply_category_spec(self, category_spec: CategorySpecificationInterface) -> None:
        """
        Apply category specification to query builder (legacy method)

        Args:
            category_spec: Category specification with joins and filters
        """
        self._apply_category_spec_with_alias(category_spec)

    def _prefix_columns_with_alias(self, sql: str, alias: str) -> str:
        """
        Add table alias prefix to column names in SQL

        Args:
            sql: SQL string to modify
            alias: Table alias to use

        Returns:
            Modified SQL string with prefixed columns
        """
        replacements = {
            'year >=': f'{alias}.year >=',
            'year <=': f'{alias}.year <=',
            'gender IN': f'{alias}.gender IN',
            'inventory.is_active': 'i.is_active',
            'inventory.is_in_stock': 'i.is_in_stock',
            'inventory.id': 'i.id',
            'COALESCE(inventory.sale_price, inventory.base_price)': 'COALESCE(i.sale_price, i.base_price)'
        }

        for old, new in replacements.items():
            sql = sql.replace(old, new)

        return sql

    def _prefix_ordering_fields(self, ordering_sql: str) -> str:
        """
        Add table alias prefix to ordering fields

        Args:
            ordering_sql: Ordering SQL to modify

        Returns:
            Modified ordering SQL with table prefixes
        """
        parts = []

        current_part = ""
        paren_count = 0

        for char in ordering_sql:
            if char == '(':
                paren_count += 1
            elif char == ')':
                paren_count -= 1
            elif char == ',' and paren_count == 0:
                parts.append(current_part.strip())
                current_part = ""
                continue
            current_part += char

        if current_part.strip():
            parts.append(current_part.strip())

        processed_parts = []
        for part in parts:
            if 'COALESCE' in part:
                processed_parts.append(part)
            else:
                part = re.sub(r'\bproduct_id\b', 'p.product_id', part)
                part = re.sub(r'\byear\b', 'p.year', part)
                part = re.sub(r'\bid\b', 'p.product_id', part)
                processed_parts.append(part)

        return ', '.join(processed_parts)

    def _build_product_dto_from_row(self, row: tuple) -> ProductDTO:
        """
        Build ProductDTO from database row including inventory data

        Args:
            row: Database result row

        Returns:
            ProductDTO with inventory data if available
        """
        product_id = int(row[0])
        gender = row[1]
        year = int(row[2])
        product_display_name = row[3]
        image_url = row[4]
        slug = row[5]

        inventory = None
        if row[6] is not None:
            inventory = InventoryDTO(
                id=int(row[6]),
                product_id=product_id,
                base_price=Decimal(str(row[7])),
                sale_price=Decimal(str(row[8])) if row[8] is not None else None,
                currency=row[9],
                stock_quantity=int(row[10]),
                reserved_quantity=int(row[11]),
                available_quantity=int(row[12]),
                is_active=bool(row[13]),
                is_in_stock=bool(row[14]),
                created_at=row[15],
                updated_at=row[16]
            )

        return ProductDTO(
            product_id=product_id,
            gender=gender,
            year=year,
            product_display_name=product_display_name,
            image_url=image_url,
            slug=slug,
            inventory=inventory
        )

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

    def _safe_alias_replace(self, sql: str, column_name: str, alias: str) -> str:
        """
        Safely replace column name with aliased version only if not already aliased

        Args:
            sql: SQL string to modify
            column_name: Column name to replace (e.g., 'product_display_name')
            alias: Table alias to add (e.g., 'p')

        Returns:
            Modified SQL string with safe alias replacement
        """
        aliased_column = f"{alias}.{column_name}"

        if aliased_column not in sql and column_name in sql:
            sql = sql.replace(column_name, aliased_column)

        return sql
