from abc import ABC, abstractmethod
from typing import Any


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


class PaginationSpecificationInterface(ABC):
    """Interface for pagination specifications"""

    @abstractmethod
    def get_offset(self) -> int:
        """Get offset for pagination"""
        pass

    @abstractmethod
    def get_limit(self) -> int:
        """Get limit for pagination"""
        pass


class OrderingSpecificationInterface(ABC):
    """Interface for ordering specifications"""

    @abstractmethod
    def get_ordering_fields(self) -> list[str]:
        """Get list of ordering fields"""
        pass
