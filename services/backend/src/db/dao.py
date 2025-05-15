from typing import (
    Any,
    List,
    Optional,
    TypeVar,
    Type,
    Union,
    Dict
)

from psycopg.rows import dict_row, class_row

from db.connection import AsyncConnectionPool
from db.interfaces import DAOInterface

T = TypeVar('T')


class PostgreSQLDAO(DAOInterface):
    """Data Access Object for PostgreSQL database operations"""

    def __init__(self, connection_pool: AsyncConnectionPool):
        self._connection_pool = connection_pool

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
        params = params or []

        row_factory = None
        if as_dict:
            row_factory = dict_row
        elif model_class:
            row_factory = class_row(model_class)

        async with self._connection_pool.connection() as conn:
            async with conn.cursor(row_factory=row_factory) as cursor:
                await cursor.execute(query, params)

                if not fetch or cursor.description is None:
                    return None

                if fetch_one:
                    return await cursor.fetchone()
                else:
                    return await cursor.fetchall()
