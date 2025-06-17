from abc import ABC, abstractmethod
from typing import Any, List, Optional, TypeVar, Type, Union, Dict, Self, Tuple

from psycopg import IsolationLevel

T = TypeVar('T')


class DAOInterface(ABC):
    """Interface for Data Access Objects"""

    @abstractmethod
    async def execute(
            self,
            query: str,
            params: Optional[List[Any]] = None,
            fetch: bool = True,
            fetch_one: bool = False,
            as_dict: bool = False,
            model_class: Optional[Type[T]] = None
    ) -> Union[List[Any], Dict[str, Any], T, List[T], None]:
        """
        Execute a query and optionally fetch results

        Args:
            query: SQL query to execute
            params: Query parameters
            fetch: Whether to fetch any results
            fetch_one: If True, fetch only one row
            as_dict: If True, return results as dictionaries
            model_class: Optional class type to map results

        Returns:
            Query results based on the options specified
        """
        pass

    @abstractmethod
    async def begin_transaction(self, isolation_level: Optional[IsolationLevel] = None):
        """Begin database transaction"""
        pass

    @abstractmethod
    async def commit_transaction(self):
        """Commit database transaction"""
        pass

    @abstractmethod
    async def rollback_transaction(self):
        """Rollback database transaction"""
        pass


class SQLQueryBuilderInterface(ABC):
    """Interface for SQL query builder"""

    @abstractmethod
    def select(self, *fields) -> Self:
        """Add fields to SELECT clause"""
        pass

    @abstractmethod
    def from_table(self, table_name: str) -> Self:
        """Set FROM table with optional alias"""
        pass

    @abstractmethod
    def where(self, condition: str, *params) -> Self:
        """Add condition to WHERE clause with params"""
        pass

    @abstractmethod
    def order_by(self, clause: str, *params) -> Self:
        """Add clause to ORDER BY section with params"""
        pass

    @abstractmethod
    def limit(self, limit_value: int) -> Self:
        """Set LIMIT value"""
        pass

    @abstractmethod
    def offset(self, offset_value: int) -> Self:
        """Set OFFSET value"""
        pass

    @abstractmethod
    def build(self) -> Tuple[str, List[Any]]:
        """Build the final SQL query and params list"""
        pass

    @abstractmethod
    def build_count(self) -> Tuple[str, List[Any]]:
        """Build COUNT query with the same conditions"""
        pass

    @abstractmethod
    def reset(self) -> Self:
        """Reset the builder state to initial values"""
        pass

    @abstractmethod
    def join(self, join_clause: str) -> Self:
        """Add JOIN clause to query"""
        pass

    @abstractmethod
    def get_where_conditions(self) -> List[str]:
        """Get current WHERE conditions"""
        pass

    @abstractmethod
    def get_params(self) -> List[Any]:
        """Get current parameters"""
        pass
