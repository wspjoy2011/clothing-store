from typing import Any, Dict, List, Optional, Type, TypeVar, Union

from psycopg import AsyncConnection
from psycopg.rows import class_row, dict_row
from psycopg_pool import AsyncConnectionPool

from db.interfaces import DAOInterface
from db.transaction import get_current_transaction
from settings.logging_config import get_logger

logger = get_logger(__name__, "db")

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
        row_factory = None
        if as_dict:
            row_factory = dict_row
        elif model_class:
            row_factory = class_row(model_class)

        transaction = get_current_transaction()
        if transaction is not None:
            logger.debug("Executing query within transaction context")
            return await self._run(transaction.connection, query, params, fetch, fetch_one, row_factory)

        logger.debug("Executing query without transaction context")
        async with self._connection_pool.connection() as connection:
            return await self._run(connection, query, params, fetch, fetch_one, row_factory)

    async def execute_write(self, query: str, params: Optional[List[Any]] = None) -> int:
        """
        Execute a statement that changes rows and report how many it changed

        A caller deciding whether the change happened cannot use the absence of an
        exception: a statement matching no row succeeds and changes nothing.

        Args:
            query: SQL statement to execute
            params: Statement parameters

        Returns:
            Number of rows the statement affected
        """
        transaction = get_current_transaction()
        if transaction is not None:
            logger.debug("Executing write within transaction context")
            return await self._run_write(transaction.connection, query, params)

        logger.debug("Executing write without transaction context")
        async with self._connection_pool.connection() as connection:
            return await self._run_write(connection, query, params)

    @staticmethod
    async def _run_write(
            connection: AsyncConnection,
            query: str,
            params: Optional[List[Any]]
    ) -> int:
        """
        Execute a changing statement on the given connection

        Args:
            connection: Connection to run the statement on
            query: SQL statement to execute
            params: Statement parameters

        Returns:
            Number of rows the statement affected
        """
        async with connection.cursor() as cursor:
            await cursor.execute(query, params or [])
            return cursor.rowcount

    @staticmethod
    async def _run(
            connection: AsyncConnection,
            query: str,
            params: Optional[List[Any]],
            fetch: bool,
            fetch_one: bool,
            row_factory: Optional[Any]
    ) -> Union[List[Any], Dict[str, Any], T, List[T], None]:
        """
        Execute a query on the given connection

        Args:
            connection: Connection to run the query on
            query: SQL query to execute
            params: Query parameters
            fetch: Whether to fetch any results
            fetch_one: If True, fetch only one row
            row_factory: Optional psycopg row factory for result mapping

        Returns:
            Query results based on the options specified
        """
        async with connection.cursor(row_factory=row_factory) as cursor:
            await cursor.execute(query, params or [])

            if not fetch or cursor.description is None:
                return None

            if fetch_one:
                return await cursor.fetchone()

            return await cursor.fetchall()
