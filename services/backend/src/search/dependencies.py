from functools import lru_cache
from typing import AsyncGenerator
from contextlib import asynccontextmanager

from search.autocomplete import ElasticsearchAutocompleteClient
from search.interfaces import AutocompleteClientInterface
from settings.config import config
from settings.logging_config import get_logger

logger = get_logger(__name__, "elasticsearch")


@lru_cache()
def _get_autocomplete_client_instance() -> ElasticsearchAutocompleteClient:
    """
    Get singleton autocomplete client instance.

    Returns:
        Configured autocomplete client instance
    """
    return ElasticsearchAutocompleteClient(
        elasticsearch_url=config.ELASTICSEARCH_URL,
        elasticsearch_auth=config.ELASTICSEARCH_AUTH,
        products_index=config.ELASTICSEARCH_PRODUCTS_INDEX
    )


def get_autocomplete_client() -> AutocompleteClientInterface:
    """
    Dependency injection for autocomplete client.

    Returns:
        Configured autocomplete client instance
    """
    client = _get_autocomplete_client_instance()
    logger.debug("Providing autocomplete client dependency")
    return client


async def cleanup_autocomplete_client():
    """
    Cleanup function to close autocomplete client at application shutdown.
    Call this in FastAPI lifespan or shutdown event.
    """
    try:
        client = _get_autocomplete_client_instance()
        await client.close()
        logger.info("Autocomplete client cleaned up successfully")
    except Exception as e:
        logger.error(f"Error during autocomplete client cleanup: {e}")
