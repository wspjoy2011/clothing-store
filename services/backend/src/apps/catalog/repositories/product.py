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

    async def get_available_filters(self) -> Optional[FiltersDTO]:
        count_result = await self._dao.execute(
            f"SELECT COUNT(*) FROM {self.APP_NAME}_products", [], fetch_one=True
        )

        if not count_result or count_result[0] == 0:
            return None

        gender_result = await self._dao.execute(
            f"SELECT DISTINCT gender FROM {self.APP_NAME}_products", []
        )
        gender_values = [row[0] for row in gender_result] if gender_result else []

        year_result = await self._dao.execute(
            f"SELECT MIN(year), MAX(year) FROM {self.APP_NAME}_products WHERE year IS NOT NULL",
            [],
            fetch_one=True
        )
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
