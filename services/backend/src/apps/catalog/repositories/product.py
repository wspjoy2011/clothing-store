from typing import Optional

from db.connection import AsyncConnectionPool

from apps.catalog.dto.products import ProductDTO
from apps.catalog.interfaces.repositories import ProductRepositoryInterface
from apps.catalog.interfaces.specifications import PaginationSpecificationInterface, SpecificationInterface, \
    OrderingSpecificationInterface


class ProductRepository(ProductRepositoryInterface):
    def __init__(self, connection_pool: AsyncConnectionPool):
        self._connection_pool = connection_pool

    async def get_products_with_specifications(
            self,
            pagination_spec: PaginationSpecificationInterface,
            ordering_spec: Optional[OrderingSpecificationInterface] = None
    ) -> list[ProductDTO]:
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

        async with self._connection_pool.connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(base_query, tuple(params))
                result = await cursor.fetchall()

            return [
                ProductDTO(
                    product_id=row[0],
                    gender=row[1],
                    year=row[2],
                    product_display_name=row[3],
                    image_url=row[4],
                )
                for row in result
            ]

    async def get_products_count(self) -> int:
        query = "SELECT COUNT(*) FROM products;"
        async with self._connection_pool.connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query)

                result = await cursor.fetchone()
                if result:
                    return result[0]
                return 0
