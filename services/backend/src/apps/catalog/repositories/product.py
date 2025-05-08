from db.connection import AsyncConnectionPool

from apps.catalog.dto.products import ProductDTO
from apps.catalog.interfaces.repositories import ProductRepositoryInterface


class ProductRepository(ProductRepositoryInterface):
    def __init__(self, connection_pool: AsyncConnectionPool):
        self._connection_pool = connection_pool

    async def get_products_with_pagination(self, offset: int, limit: int) -> list[ProductDTO]:
        query = """
        SELECT 
            product_id,
            gender,
            year,
            product_display_name,
            image_url
        FROM products
        OFFSET %s LIMIT %s;
        """

        async with self._connection_pool.connection() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(query, (offset, limit))
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
