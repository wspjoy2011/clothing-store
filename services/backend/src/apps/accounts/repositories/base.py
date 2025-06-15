from typing import Optional, List

import psycopg

from apps.accounts.repositories.exceptions import DatabaseQueryError
from apps.accounts.repositories.mixins import AccountsRepositoryMixin
from db.interfaces import DAOInterface, SQLQueryBuilderInterface
from settings.logging_config import get_logger

logger = get_logger(__name__, "accounts")


class BaseRepository(AccountsRepositoryMixin):
    """Base repository class with common database operations"""

    APP_NAME = "accounts"

    def __init__(self, dao: DAOInterface, query_builder: SQLQueryBuilderInterface):
        """
        Initialize base repository

        Args:
            dao: Data Access Object for database operations
            query_builder: SQL query builder for constructing queries
        """
        self._dao = dao
        self._query_builder = query_builder

    async def _execute_query_single(self, log_prefix: str) -> Optional[tuple]:
        """Execute query and return single result"""
        query, params = self._query_builder.build()
        logger.info(f"{log_prefix} query: {query}")
        logger.info(f"{log_prefix} params: {params}")

        try:
            return await self._dao.execute(query, params, fetch_one=True)
        except (psycopg.Error, psycopg.DatabaseError) as e:
            logger.error(f"Database error in query: {e}")
            raise DatabaseQueryError(f"{log_prefix} failed", e)
        except Exception as e:
            logger.error(f"Unexpected error in query: {e}")
            raise DatabaseQueryError(f"{log_prefix} failed with unexpected error", e)

    async def _execute_query_multiple(self, log_prefix: str) -> List[tuple]:
        """Execute query and return multiple results"""
        query, params = self._query_builder.build()
        logger.info(f"{log_prefix} query: {query}")
        logger.info(f"{log_prefix} params: {params}")

        try:
            result = await self._dao.execute(query, params)
        except (psycopg.Error, psycopg.DatabaseError) as e:
            logger.error(f"Database error in query: {e}")
            raise DatabaseQueryError(f"{log_prefix} failed", e)
        except Exception as e:
            logger.error(f"Unexpected error in query: {e}")
            raise DatabaseQueryError(f"{log_prefix} failed with unexpected error", e)
        else:
            return result or []

    async def _execute_count_query(self, log_prefix: str) -> int:
        """Execute count query"""
        query, params = self._query_builder.build_count()
        logger.info(f"{log_prefix} query: {query}")
        logger.info(f"{log_prefix} params: {params}")

        try:
            result = await self._dao.execute(query, params, fetch_one=True)
        except (psycopg.Error, psycopg.DatabaseError) as e:
            logger.error(f"Database error in count query: {e}")
            raise DatabaseQueryError(f"{log_prefix} failed", e)
        except Exception as e:
            logger.error(f"Unexpected error in count query: {e}")
            raise DatabaseQueryError(f"{log_prefix} failed with unexpected error", e)
        else:
            return int(result[0]) if result else 0

    async def _execute_custom_query_single(self, query: str, params: List, log_prefix: str) -> Optional[tuple]:
        """Execute custom query and return single result"""
        logger.info(f"{log_prefix} query: {query}")
        logger.info(f"{log_prefix} params: {params}")

        try:
            return await self._dao.execute(query, params, fetch_one=True)
        except (psycopg.Error, psycopg.DatabaseError) as e:
            logger.error(f"Database error in custom query: {e}")
            raise DatabaseQueryError(f"{log_prefix} failed", e)
        except Exception as e:
            logger.error(f"Unexpected error in custom query: {e}")
            raise DatabaseQueryError(f"{log_prefix} failed with unexpected error", e)

    async def _execute_custom_query_multiple(self, query: str, params: List, log_prefix: str) -> List[tuple]:
        """Execute custom query and return multiple results"""
        logger.info(f"{log_prefix} query: {query}")
        logger.info(f"{log_prefix} params: {params}")

        try:
            result = await self._dao.execute(query, params)
        except (psycopg.Error, psycopg.DatabaseError) as e:
            logger.error(f"Database error in custom query: {e}")
            raise DatabaseQueryError(f"{log_prefix} failed", e)
        except Exception as e:
            logger.error(f"Unexpected error in custom query: {e}")
            raise DatabaseQueryError(f"{log_prefix} failed with unexpected error", e)
        else:
            return result or []

    async def _execute_custom_update_query(self, query: str, params: List, log_prefix: str) -> bool:
        """Execute custom UPDATE/DELETE query and return number of affected rows"""
        logger.info(f"{log_prefix} query: {query}")
        logger.info(f"{log_prefix} params: {params}")

        try:
            cursor = await self._dao.execute(query, params)
        except (psycopg.Error, psycopg.DatabaseError) as e:
            logger.error(f"Database error in custom update query: {e}")
            raise DatabaseQueryError(f"{log_prefix} failed", e)
        except Exception as e:
            logger.error(f"Unexpected error in custom update query: {e}")
            raise DatabaseQueryError(f"{log_prefix} failed with unexpected error", e)
        else:
            return True

    def _build_delete_query(self, table_name: str) -> tuple[str, list]:
        """Build DELETE query using current WHERE conditions"""
        where_conditions = self._query_builder.get_where_conditions()
        params = self._query_builder.get_params()

        query = f"DELETE FROM {self.APP_NAME}_{table_name}"

        if where_conditions:
            query += f" WHERE {' AND '.join(where_conditions)}"

        return query, params
