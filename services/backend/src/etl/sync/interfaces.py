"""Interfaces for data synchronization components."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, AsyncIterable


class DataExtractorInterface(ABC):
    """Interface for data extraction from various sources."""

    @abstractmethod
    def extract_products(self) -> AsyncIterable[Dict[str, Any]]:
        """
        Extract product data from source.
        
        Returns:
            AsyncIterable of product data dictionaries
        """
        pass

    @abstractmethod
    async def get_products_count(self) -> int:
        """
        Get total count of products to extract.
        
        Returns:
            Total number of products
        """
        pass


class DataLoaderInterface(ABC):
    """Interface for data loading to various destinations."""

    @abstractmethod
    async def clear_index(self) -> None:
        """Clear all data from the destination index."""
        pass

    @abstractmethod
    async def bulk_load_products(self, products: List[Dict[str, Any]]) -> None:
        """
        Load products data to destination in bulk.
        
        Args:
            products: List of product data dictionaries
        """
        pass

    @abstractmethod
    async def create_index_if_not_exists(self) -> None:
        """Create index if it doesn't exist."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if destination is healthy and accessible.
        
        Returns:
            True if healthy, False otherwise
        """
        pass


class DataMigratorInterface(ABC):
    """Interface for data migration orchestration."""

    @abstractmethod
    async def migrate_products(self, batch_size: int = 1000) -> None:
        """
        Orchestrate full product data migration.
        
        Args:
            batch_size: Number of products to process in each batch
        """
        pass
