from typing import (
    Any,
    List,
    Optional,
    TypeVar,
    Type,
    Union,
    Dict
)
import traceback

from psycopg.rows import dict_row, class_row
from psycopg import IsolationLevel

from db.connection import AsyncConnectionPool
from db.interfaces import DAOInterface
from db.transaction_context import _current_transaction
from settings.logging_config import get_logger

logger = get_logger(__name__, "db")

T = TypeVar('T')


class PostgreSQLDAO(DAOInterface):
    """Data Access Object for PostgreSQL database operations with transaction support"""

    def __init__(self, connection_pool: AsyncConnectionPool):
        self._connection_pool = connection_pool
        self._current_connection = None
        self._current_transaction = None
        self._connection_context = None

    async def begin_transaction(self, isolation_level: Optional[IsolationLevel] = None):
        """Begin database transaction"""
        try:
            logger.debug("Beginning database transaction...")

            if self._current_connection is None:
                logger.debug("Getting connection from pool...")
                self._connection_context = self._connection_pool.connection()
                self._current_connection = await self._connection_context.__aenter__()

                if isolation_level is not None:
                    logger.debug(f"Setting isolation level to: {isolation_level.name}")
                    self._current_connection.isolation_level = isolation_level

                logger.debug("Connection obtained from pool")

            if self._current_transaction is None:
                logger.debug("Starting transaction on connection...")
                self._current_transaction = self._current_connection.transaction()
                await self._current_transaction.__aenter__()
                logger.info("Database transaction started successfully")

        except Exception as e:
            logger.error(f"Failed to begin transaction: {e}")
            logger.error(f"Begin transaction traceback: {traceback.format_exc()}")
            await self._cleanup_connection()
            raise

    async def commit_transaction(self):
        """Commit database transaction"""
        try:
            logger.debug("Committing database transaction...")

            if self._current_transaction:
                await self._current_transaction.__aexit__(None, None, None)
                self._current_transaction = None
                logger.info("Database transaction committed successfully")

            await self._cleanup_connection()

        except Exception as e:
            logger.error(f"Failed to commit transaction: {e}")
            logger.error(f"Commit traceback: {traceback.format_exc()}")
            await self._cleanup_connection()
            raise

    async def rollback_transaction(self):
        """Rollback database transaction"""
        try:
            logger.debug("Rolling back database transaction...")

            if self._current_transaction:
                await self._current_transaction.__aexit__(Exception, Exception("Manual rollback"), None)
                self._current_transaction = None
                logger.info("Database transaction rolled back successfully")

            await self._cleanup_connection()

        except Exception as e:
            logger.error(f"Failed to rollback transaction: {e}")
            logger.error(f"Rollback traceback: {traceback.format_exc()}")
            await self._cleanup_connection()
            raise

    async def _cleanup_connection(self):
        """Clean up connection and return to pool"""
        try:
            if self._connection_context and self._current_connection:
                await self._connection_context.__aexit__(None, None, None)
                logger.debug("Connection returned to pool")

            self._current_connection = None
            self._connection_context = None

        except Exception as e:
            logger.warning(f"Error during connection cleanup: {e}")
            self._current_connection = None
            self._connection_context = None

    async def execute(
            self,
            query: str,
            params: Optional[List[Any]] = None,
            fetch: bool = True,
            fetch_one: bool = False,
            as_dict: bool = False,
            model_class: Optional[Type[T]] = None
    ) -> Union[List[Any], Dict[str, Any], T, List[T], None]:
        """Execute a query and optionally fetch results"""
        params = params or []

        row_factory = None
        if as_dict:
            row_factory = dict_row
        elif model_class:
            row_factory = class_row(model_class)

        current_tx = _current_transaction.get()
        if current_tx and current_tx._is_active:
            logger.debug("Executing query within transaction context")
            conn = current_tx.get_connection()
            if conn is None:
                raise RuntimeError("Transaction context is active but connection is None")

            async with conn.cursor(row_factory=row_factory) as cursor:
                await cursor.execute(query, params)

                if not fetch or cursor.description is None:
                    return None

                if fetch_one:
                    return await cursor.fetchone()
                else:
                    return await cursor.fetchall()
        else:
            logger.debug("Executing query without transaction context")
            async with self._connection_pool.connection() as conn:
                async with conn.cursor(row_factory=row_factory) as cursor:
                    await cursor.execute(query, params)

                    if not fetch or cursor.description is None:
                        return None

                    if fetch_one:
                        return await cursor.fetchone()
                    else:
                        return await cursor.fetchall()
