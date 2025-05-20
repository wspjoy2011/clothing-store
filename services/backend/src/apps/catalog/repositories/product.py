from typing import Optional, List, Any

from apps.catalog.dto.filters import FiltersDTO, CheckboxFilterDTO, RangeFilterDTO
from apps.catalog.dto.products import ProductDTO
from apps.catalog.interfaces.repositories import ProductRepositoryInterface
from apps.catalog.interfaces.specifications import (
    PaginationSpecificationInterface,
    OrderingSpecificationInterface,
    FilterSpecificationInterface,
    SearchSpecificationInterface
)
from db.interfaces import DAOInterface, SQLQueryBuilderInterface
from settings.logging_config import get_logger

logger = get_logger(__name__, "app")


class ProductRepository(ProductRepositoryInterface):
    APP_NAME = "catalog"

    def __init__(self, dao: DAOInterface, query_builder: SQLQueryBuilderInterface):
        self._dao = dao
        self._query_builder = query_builder

    async def get_products_with_specifications(
        self,
        pagination_spec: PaginationSpecificationInterface,
        ordering_spec: Optional[OrderingSpecificationInterface] = None,
        filter_spec: Optional[FilterSpecificationInterface] = None,
        search_spec: Optional[SearchSpecificationInterface] = None
    ) -> List[ProductDTO]:

        self._prepare_query_builder(filter_spec, search_spec, ordering_spec)

        self._query_builder.limit(pagination_spec.get_limit()).offset(pagination_spec.get_offset())

        query, params = self._query_builder.build()
        logger.info(f"Final query: {query}")
        logger.info(f"Final params: {params}")

        result = await self._dao.execute(query, params)

        return [
            ProductDTO(
                product_id=int(row[0]),
                gender=row[1],
                year=int(row[2]),
                product_display_name=row[3],
                image_url=row[4],
            )
            for row in (result or [])
        ]

    async def get_products_count(
            self,
            filter_spec: Optional[FilterSpecificationInterface] = None,
            search_spec: Optional[SearchSpecificationInterface] = None
    ) -> int:

        self._query_builder.reset()

        if filter_spec and not filter_spec.is_empty():
            filter_sql, filter_params = filter_spec.to_sql()
            self._parse_sql_conditions(filter_sql, filter_params)

        if search_spec and not search_spec.is_empty():
            search_sql, search_params = search_spec.to_sql()
            where_sql, _ = self._split_search_sql(search_sql)

            self._parse_sql_conditions(where_sql, search_params[:1])

        query, params = self._query_builder.build_count()
        logger.info(f"Final count query: {query}")
        logger.info(f"Final count params: {params}")

        result = await self._dao.execute(query, params, fetch_one=True)
        return result[0] if result else 0

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

    async def _get_all_filters(self) -> Optional[FiltersDTO]:
        """
        Get all available filters without additional filtering

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
        Get available filters based on search query results

        Args:
            search_spec: Search specification for filtering

        Returns:
            FiltersDTO object containing filtered available filters or None if no results
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

        self._query_builder.reset().select("DISTINCT gender")

        self._parse_sql_conditions(where_sql, search_params[:1])

        self._query_builder.where("gender IS NOT NULL")

        gender_query, gender_params = self._query_builder.build()
        logger.info(f"Filtered filters gender query: {gender_query}")
        logger.info(f"Filtered filters gender params: {gender_params}")

        gender_result = await self._dao.execute(gender_query, gender_params)
        gender_values = [row[0] for row in gender_result] if gender_result else []

        self._query_builder.reset().select("MIN(year)", "MAX(year)")

        self._parse_sql_conditions(where_sql, search_params[:1])

        self._query_builder.where("year IS NOT NULL")

        year_query, year_params = self._query_builder.build()
        logger.info(f"Filtered filters year query: {year_query}")
        logger.info(f"Filtered filters year params: {year_params}")

        year_result = await self._dao.execute(year_query, year_params, fetch_one=True)
        min_year, max_year = year_result if year_result else (None, None)

        return FiltersDTO(
            gender=CheckboxFilterDTO(values=gender_values) if gender_values else None,
            year=RangeFilterDTO(min=min_year, max=max_year) if min_year and max_year else None
        )

    def _prepare_query_builder(
            self,
            filter_spec: Optional[FilterSpecificationInterface],
            search_spec: Optional[SearchSpecificationInterface],
            ordering_spec: Optional[OrderingSpecificationInterface] = None
    ) -> None:

        self._query_builder.reset().select(
            "product_id", "gender", "year", "product_display_name", "image_url"
        )

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

    def _parse_sql_conditions(self, sql_conditions: str, params: List[Any]) -> None:
        if sql_conditions.startswith("WHERE"):
            conditions_text = sql_conditions.replace("WHERE", "").strip()
            self._query_builder.where(conditions_text, *params)

    @staticmethod
    def _split_search_sql(search_sql: str) -> (str, str):
        if "ORDER BY" in search_sql:
            where_part, order_by_part = search_sql.split("ORDER BY", 1)
            return where_part.strip(), order_by_part.strip()
        return search_sql.strip(), ""
