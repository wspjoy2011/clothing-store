from typing import Optional

from apps.catalog.dto.products import ProductDTO
from apps.catalog.interfaces.repositories import ProductRepositoryInterface
from apps.catalog.interfaces.specifications import (
    PaginationSpecificationInterface,
    SpecificationInterface,
    OrderingSpecificationInterface
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
            ordering_spec: Optional[OrderingSpecificationInterface] = None
    ) -> list[ProductDTO]:
        """
        Get products using pagination and optional ordering specifications

        Args:
            pagination_spec: Specification for pagination
            ordering_spec: Optional specification for ordering results

        Returns:
            List of product DTOs
        """
        base_query = """
                     SELECT product_id, \
                            gender, \
                            year, \
                            product_display_name, \
                            image_url
                     FROM products \
                     """

        params = []

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

    async def get_products_count(self) -> int:
        """
        Get total count of products

        Returns:
            Number of products in the database
        """
        query = "SELECT COUNT(*) FROM products;"
        result = await self._dao.execute(query, fetch_one=True)
        return result[0] if result else 0
