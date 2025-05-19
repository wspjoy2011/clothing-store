from abc import ABC, abstractmethod
from typing import Any, Optional


class SpecificationInterface(ABC):
    """Base interface for specifications"""

    @abstractmethod
    def to_sql(self) -> tuple[str, list[Any]]:
        """
        Convert specification to SQL clause and parameters

        Returns:
            tuple[str, list[Any]]: SQL part, list of parameters
        """
        pass


class PaginationSpecificationInterface(SpecificationInterface):
    """Interface for pagination specifications"""

    @abstractmethod
    def get_offset(self) -> int:
        """Get offset for pagination"""
        pass

    @abstractmethod
    def get_limit(self) -> int:
        """Get limit for pagination"""
        pass


class OrderingSpecificationInterface(SpecificationInterface):
    """Interface for ordering specifications"""

    @abstractmethod
    def get_ordering_fields(self) -> list[str]:
        """Get list of ordering fields"""
        pass


class FilterSpecificationInterface(SpecificationInterface):
    """Interface for filtering specifications"""

    @abstractmethod
    def add_filter(self, field: str, value: Any) -> None:
        """
        Add a filter criterion

        Args:
            field: Field name to filter on
            value: Value to filter by
        """
        pass

    @abstractmethod
    def is_empty(self) -> bool:
        """
        Check if filter specification has any filters

        Returns:
            True if no filters are defined, False otherwise
        """
        pass


class SearchSpecificationInterface(SpecificationInterface):
    """Interface for search specifications."""

    @property
    @abstractmethod
    def query(self) -> Optional[str]:
        """Get the search query."""
        pass

    @abstractmethod
    def is_empty(self) -> bool:
        """Check if the search specification is empty."""
        pass
