"""Data extractors for various sources."""

from typing import Dict, Any, AsyncIterable
from psycopg import AsyncConnection
from psycopg import sql

from etl.sync.interfaces import DataExtractorInterface
from etl.sync.exceptions import DataExtractionError
from settings.logging_config import get_logger

logger = get_logger(__name__, "sync_extractors")


class PostgreSQLProductExtractor(DataExtractorInterface):
    """Extractor for product data from PostgreSQL."""

    def __init__(self, connection: AsyncConnection):
        """
        Initialize PostgreSQL product extractor.
        
        Args:
            connection: PostgreSQL async connection from pool
        """
        self._connection = connection
        logger.info("PostgreSQL product extractor initialized")

    def extract_products(self) -> AsyncIterable[Dict[str, Any]]:
        """
        Extract product data from catalog_products table.
        
        Returns:
            AsyncIterable of product data dictionaries with id and product_display_name
        """
        return self._extract_products_generator()

    async def _extract_products_generator(self) -> AsyncIterable[Dict[str, Any]]:
        """
        Internal generator for extracting product data.
        
        Yields:
            Product data dictionaries with id and product_display_name
            
        Raises:
            DataExtractionError: When extraction fails
        """
        try:
            logger.info("Starting product extraction from PostgreSQL")

            query = sql.SQL("""
                            SELECT id, product_display_name
                            FROM catalog_products
                            WHERE product_display_name IS NOT NULL
                              AND TRIM(product_display_name) != ''
                            ORDER BY id
                            """)

            async with self._connection.cursor() as cursor:
                await cursor.execute(query)

                count = 0
                async for row in cursor:
                    count += 1
                    yield {
                        "id": row[0],
                        "product_display_name": row[1].strip()
                    }

                    if count % 1000 == 0:
                        logger.info(f"Extracted {count} products...")

                logger.info(f"Product extraction completed. Total: {count} products")

        except Exception as e:
            logger.error(f"Failed to extract products from PostgreSQL: {e}")
            raise DataExtractionError(f"Product extraction failed: {str(e)}", e)

    async def get_products_count(self) -> int:
        """
        Get total count of products to extract.
        
        Returns:
            Total number of valid products
            
        Raises:
            DataExtractionError: When count query fails
        """
        try:
            query = sql.SQL("""
                            SELECT COUNT(*)
                            FROM catalog_products
                            WHERE product_display_name IS NOT NULL
                              AND TRIM(product_display_name) != ''
                            """)

            async with self._connection.cursor() as cursor:
                await cursor.execute(query)
                row = await cursor.fetchone()
                count = row[0] if row else 0

                logger.info(f"Total products to extract: {count}")
                return count

        except Exception as e:
            logger.error(f"Failed to get products count: {e}")
            raise DataExtractionError(f"Products count query failed: {str(e)}", e)
