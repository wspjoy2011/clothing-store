from abc import ABC, abstractmethod
from typing import Any, List, Optional, TypeVar, Type, Union, Dict

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
