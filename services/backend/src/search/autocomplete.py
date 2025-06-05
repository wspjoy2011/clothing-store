from typing import List, AsyncGenerator
from contextlib import asynccontextmanager
from elasticsearch import AsyncElasticsearch, ApiError, ConnectionError

from search.interfaces import AutocompleteClientInterface
from search.exceptions import (
    ElasticsearchConnectionError,
    AutocompleteError
)
from settings.logging_config import get_logger

logger = get_logger(__name__, "elasticsearch")


class ElasticsearchAutocompleteClient(AutocompleteClientInterface):
    """
    Elasticsearch-based autocomplete client for product suggestions.
    """

    def __init__(
            self,
            elasticsearch_url: str,
            elasticsearch_auth: tuple[str, str],
            products_index: str,
            **client_kwargs
    ):
        """
        Initialize Elasticsearch autocomplete client.

        Args:
            elasticsearch_url: Elasticsearch connection URL
            elasticsearch_auth: Authentication tuple (username, password)
            products_index: Name of the products index
            **client_kwargs: Additional client configuration
        """
        self._elasticsearch_url = elasticsearch_url
        self._elasticsearch_auth = elasticsearch_auth
        self._products_index = products_index
        self._client_config = {
            "hosts": [elasticsearch_url],
            "http_auth": elasticsearch_auth,
            "verify_certs": False,
            "ssl_show_warn": False,
            "request_timeout": 30,
            "retry_on_timeout": True,
            "max_retries": 3,
            **client_kwargs
        }
        self._client: AsyncElasticsearch | None = None
        logger.info(f"Initialized Elasticsearch client for URL: {elasticsearch_url}")

    async def _get_client(self) -> AsyncElasticsearch:
        """Get or create Elasticsearch client."""
        if self._client is None:
            try:
                self._client = AsyncElasticsearch(**self._client_config)
                logger.info("Elasticsearch client created successfully")
            except Exception as e:
                logger.error(f"Failed to create Elasticsearch client: {e}")
                raise ElasticsearchConnectionError(
                    "Failed to create Elasticsearch client", e
                )
        return self._client

    @asynccontextmanager
    async def get_client_context(self) -> AsyncGenerator[AsyncElasticsearch, None]:
        """
        Async context manager for Elasticsearch client.
        Ensures proper connection cleanup.
        """
        client = None
        try:
            client = await self._get_client()
            logger.debug("Elasticsearch client context opened")
            yield client
        except ConnectionError as e:
            logger.error(f"Elasticsearch connection error: {e}")
            raise ElasticsearchConnectionError(
                "Failed to connect to Elasticsearch", e
            )
        except Exception as e:
            logger.error(f"Unexpected error in client context: {e}")
            raise
        finally:
            if client:
                logger.debug("Elasticsearch client context closed")

    async def get_suggestions(self, query: str, size: int = 10) -> List[str]:
        """
        Get product name suggestions using Elasticsearch completion suggester.

        Args:
            query: Partial product name for autocomplete
            size: Maximum number of suggestions to return

        Returns:
            List of suggested product names

        Raises:
            AutocompleteError: When autocomplete operation fails
        """
        if not query.strip():
            logger.debug("Empty query provided for autocomplete")
            return []

        logger.info(f"Getting autocomplete suggestions for query: '{query}', size: {size}")

        try:
            async with self.get_client_context() as client:
                response = await client.search(
                    index=self._products_index,
                    body={
                        "suggest": {
                            "product_suggest": {
                                "prefix": query,
                                "completion": {
                                    "field": "product_display_name",
                                    "size": size
                                }
                            }
                        }
                    }
                )

                suggestions = []
                suggest_results = response.get("suggest", {}).get("product_suggest", [])

                for suggest_result in suggest_results:
                    for option in suggest_result.get("options", []):
                        text = option.get("text")
                        if text and text not in suggestions:
                            suggestions.append(text)

                logger.info(f"Retrieved {len(suggestions)} suggestions for query: '{query}'")
                return suggestions[:size]

        except ApiError as e:
            logger.error(f"Elasticsearch API error during autocomplete: {e}")
            raise AutocompleteError(f"Autocomplete query failed: {e.message}", e)
        except ConnectionError as e:
            logger.error(f"Elasticsearch connection error during autocomplete: {e}")
            raise ElasticsearchConnectionError("Connection lost during autocomplete", e)
        except Exception as e:
            logger.error(f"Unexpected error during autocomplete: {e}")
            raise AutocompleteError(f"Unexpected autocomplete error: {str(e)}", e)

    async def health_check(self) -> bool:
        """
        Check if Elasticsearch connection is healthy.

        Returns:
            True if connection is healthy, False otherwise
        """
        try:
            async with self.get_client_context() as client:
                health = await client.cluster.health()
                status = health.get("status")
                is_healthy = status in ["green", "yellow"]

                logger.info(f"Elasticsearch health check: status={status}, healthy={is_healthy}")
                return is_healthy

        except Exception as e:
            logger.warning(f"Elasticsearch health check failed: {e}")
            return False

    async def close(self):
        """Close Elasticsearch client connection."""
        if self._client:
            try:
                await self._client.close()
                logger.info("Elasticsearch client connection closed")
            except Exception as e:
                logger.error(f"Error closing Elasticsearch client: {e}")
            finally:
                self._client = None
