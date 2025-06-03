"""Data loaders for various destinations."""

from typing import List, Dict, Any
from elasticsearch import AsyncElasticsearch, NotFoundError

from etl.sync.interfaces import DataLoaderInterface
from etl.sync.exceptions import DataLoadingError, IndexOperationError
from settings.logging_config import get_logger

logger = get_logger(__name__, "sync_loaders")


class ElasticsearchProductLoader(DataLoaderInterface):
    """Loader for product data to Elasticsearch."""

    def __init__(self, client: AsyncElasticsearch, index_name: str):
        """
        Initialize Elasticsearch product loader.

        Args:
            client: Elasticsearch async client
            index_name: Name of the products index
        """
        self._client = client
        self._index_name = index_name
        logger.info(f"Elasticsearch product loader initialized for index: {index_name}")

    async def create_index_if_not_exists(self) -> None:
        """
        Create products index with proper mapping if it doesn't exist.

        Raises:
            IndexOperationError: When index creation fails
        """
        try:
            exists = await self._client.indices.exists(index=self._index_name)

            if not exists:
                logger.info(f"Creating index: {self._index_name}")

                mapping = {
                    "mappings": {
                        "properties": {
                            "product_display_name": {
                                "type": "completion",
                                "analyzer": "simple"
                            }
                        }
                    },
                    "settings": {
                        "number_of_shards": 1,
                        "number_of_replicas": 0
                    }
                }

                await self._client.indices.create(
                    index=self._index_name,
                    body=mapping
                )

                logger.info(f"Index {self._index_name} created successfully")
            else:
                logger.info(f"Index {self._index_name} already exists")

        except Exception as e:
            logger.error(f"Failed to create index {self._index_name}: {e}")
            raise IndexOperationError(f"Index creation failed: {str(e)}", e)

    async def clear_index(self) -> None:
        """
        Clear all documents from the products index.

        Raises:
            IndexOperationError: When index clearing fails
        """
        try:
            logger.info(f"Clearing index: {self._index_name}")

            await self._client.delete_by_query(
                index=self._index_name,
                body={"query": {"match_all": {}}},
                refresh=True
            )

            logger.info(f"Index {self._index_name} cleared successfully")

        except NotFoundError:
            logger.warning(f"Index {self._index_name} not found, nothing to clear")
        except Exception as e:
            logger.error(f"Failed to clear index {self._index_name}: {e}")
            raise IndexOperationError(f"Index clearing failed: {str(e)}", e)

    async def bulk_load_products(self, products: List[Dict[str, Any]]) -> None:
        """
        Load products data to Elasticsearch in bulk.

        Args:
            products: List of product data dictionaries

        Raises:
            DataLoadingError: When bulk loading fails
        """
        if not products:
            logger.debug("No products to load")
            return

        try:
            logger.info(f"Bulk loading {len(products)} products to {self._index_name}")

            operations = []
            for product in products:
                operations.extend([
                    {
                        "index": {
                            "_index": self._index_name,
                            "_id": product["id"]
                        }
                    },
                    {
                        "product_display_name": product["product_display_name"]
                    }
                ])

            response = await self._client.bulk(
                operations=operations,
                refresh=True
            )

            if response.get("errors", False):
                failed_items = [
                    item for item in response["items"]
                    if "error" in item.get("index", {})
                ]
                logger.error(f"Bulk loading had {len(failed_items)} errors")
                raise DataLoadingError(f"Bulk loading partially failed with {len(failed_items)} errors")

            logger.info(f"Successfully loaded {len(products)} products")

        except Exception as e:
            logger.error(f"Failed to bulk load products: {e}")
            raise DataLoadingError(f"Bulk loading failed: {str(e)}", e)

    async def health_check(self) -> bool:
        """
        Check if Elasticsearch is healthy and accessible.

        Returns:
            True if healthy, False otherwise
        """
        try:
            health = await self._client.cluster.health()
            status = health.get("status")
            is_healthy = status in ["green", "yellow"]

            logger.info(f"Elasticsearch health check: status={status}, healthy={is_healthy}")
            return is_healthy

        except Exception as e:
            logger.warning(f"Elasticsearch health check failed: {e}")
            return False
