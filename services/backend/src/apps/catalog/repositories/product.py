from typing import Optional

from apps.catalog.dto.filters import FiltersDTO, CheckboxFilterDTO, RangeFilterDTO
from apps.catalog.dto.products import ProductDTO
from apps.catalog.interfaces.repositories import ProductRepositoryInterface
from apps.catalog.interfaces.specifications import (
    PaginationSpecificationInterface,
    SpecificationInterface,
    OrderingSpecificationInterface,
    FilterSpecificationInterface
)
from db.interfaces import DAOInterface


class ProductRepository(ProductRepositoryInterface):
    """Repository for product data access"""

    def __init__(self, dao: DAOInterface):
        """
        Initialize product repository

        Args:
            dao: Data Access Object for database operations
        """
        self._dao = dao

    async def get_products_with_specifications(
            self,
            pagination_spec: PaginationSpecificationInterface,
            ordering_spec: Optional[OrderingSpecificationInterface] = None,
            filter_spec: Optional[FilterSpecificationInterface] = None
    ) -> list[ProductDTO]:
        """
        Get products using pagination, ordering, and filtering specifications

        Args:
            pagination_spec: Specification for pagination
            ordering_spec: Optional specification for ordering results
            filter_spec: Optional specification for filtering results

        Returns:
            List of product DTOs
        """
        base_query = """
                     SELECT product_id,
                            gender,
                            year,
                            product_display_name,
                            image_url
                     FROM products 
                     """

        params = []

        if filter_spec and isinstance(filter_spec, SpecificationInterface) and not filter_spec.is_empty():
            filter_clause, filter_params = filter_spec.to_sql()
            base_query += f" {filter_clause}"
            params.extend(filter_params)

        if ordering_spec and isinstance(ordering_spec, SpecificationInterface):
            order_clause, order_params = ordering_spec.to_sql()
            base_query += f" {order_clause}"
            params.extend(order_params)

        if isinstance(pagination_spec, SpecificationInterface):
            pagination_clause, pagination_params = pagination_spec.to_sql()
            base_query += f" {pagination_clause}"
            params.extend(pagination_params)
        else:
            base_query += " OFFSET %s LIMIT %s"
            params.extend([pagination_spec.get_offset(), pagination_spec.get_limit()])

        result = await self._dao.execute(base_query, params)

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
            filter_spec: Optional[FilterSpecificationInterface] = None
    ) -> int:
        """
        Get total count of products, optionally filtered

        Args:
            filter_spec: Optional specification for filtering results

        Returns:
            Number of products in the database
        """
        query = "SELECT COUNT(*) FROM products"
        params = []

        if filter_spec and isinstance(filter_spec, SpecificationInterface) and not filter_spec.is_empty():
            filter_clause, filter_params = filter_spec.to_sql()
            query += f" {filter_clause}"
            params.extend(filter_params)

        result = await self._dao.execute(query, params, fetch_one=True)
        return result[0] if result else 0

    async def get_available_filters(self) -> Optional[FiltersDTO]:
        """
        Get available filters and their possible values based on the actual data

        Returns:
            FiltersDTO object containing all available filters or None if catalog is empty
        """

        count_query = "SELECT COUNT(*) FROM products"
        count_result = await self._dao.execute(count_query, [], fetch_one=True)

        if not count_result or count_result[0] == 0:
            return None

        gender_query = "SELECT DISTINCT gender FROM products"
        gender_result = await self._dao.execute(gender_query, [])
        gender_values = [row[0] for row in gender_result] if gender_result else []

        year_query = "SELECT MIN(year), MAX(year) FROM products WHERE year IS NOT NULL"
        year_result = await self._dao.execute(year_query, [], fetch_one=True)
        min_year, max_year = year_result if year_result else (None, None)

        return FiltersDTO(
            gender=CheckboxFilterDTO(values=gender_values) if gender_values else None,
            year=RangeFilterDTO(min=min_year, max=max_year) if min_year and max_year else None
        )
