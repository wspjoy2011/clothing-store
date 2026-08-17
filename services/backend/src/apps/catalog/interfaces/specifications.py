from abc import ABC, abstractmethod
from typing import Any, List, Optional, Tuple

from apps.catalog.specifications.clauses import SqlClause


class SpecificationInterface(ABC):
    """Base interface for specifications

    A specification describes what to select, not how the statement is written: it
    returns predicates with their parameters and never SQL keywords, so nothing has
    to parse or rewrite its output.
    """

    @abstractmethod
    def is_empty(self) -> bool:
        """
        Check whether the specification narrows anything

        Returns:
            True when the specification contributes no criteria
        """
        pass


class ClauseSpecificationInterface(SpecificationInterface):
    """Interface for specifications contributing conditions to a statement"""

    @abstractmethod
    def to_clause(self) -> SqlClause:
        """
        Build the conditions this specification contributes

        Returns:
            Conditions, joins and the parameters they bind
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
    def to_order_by(self) -> List[str]:
        """
        Build the ordering expressions, in the order they apply

        Returns:
            Expressions already qualified and safe to place after ORDER BY
        """
        pass

    @abstractmethod
    def get_ordering_fields(self) -> List[str]:
        """Get list of ordering fields as the client asked for them"""
        pass

    @property
    @abstractmethod
    def is_default(self) -> bool:
        """
        Report whether the client asked for no particular order

        Search uses this to decide whether relevance leads the ordering or merely
        breaks ties behind the order the client chose.
        """
        pass


class FilterSpecificationInterface(ClauseSpecificationInterface):
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


class SearchSpecificationInterface(ClauseSpecificationInterface):
    """Interface for search specifications."""

    @property
    @abstractmethod
    def query(self) -> Optional[str]:
        """Get the search query."""
        pass

    @abstractmethod
    def relevance_order(self) -> Tuple[str, List[Any]]:
        """
        Build the ordering expression ranking matches by relevance

        Returns:
            Expression and the parameter it binds, empty when nothing is searched
        """
        pass


class CategorySpecificationInterface(ClauseSpecificationInterface):
    """Interface for category specifications"""
