from abc import ABC, abstractmethod
from typing import List, AsyncGenerator


class AutocompleteClientInterface(ABC):
    """
    Interface for autocomplete client using Elasticsearch.
    """

    @abstractmethod
    async def get_suggestions(self, query: str, size: int = 10) -> List[str]:
        """
        Get product name suggestions based on partial input.

        Args:
            query: Partial product name for autocomplete
            size: Maximum number of suggestions to return

        Returns:
            List of suggested product names
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if Elasticsearch connection is healthy.

        Returns:
            True if connection is healthy, False otherwise
        """
        pass

    @abstractmethod
    async def get_client_context(self) -> AsyncGenerator[object, None]:
        """
        Async context manager for client connection.
        Ensures proper connection lifecycle management.

        Yields:
            Client instance for operations
        """
        pass

    @abstractmethod
    async def close(self) -> None:
        """
        Close client connection and cleanup resources.
        Should be called at application shutdown.
        """
        pass
