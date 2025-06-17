from typing import Optional

from fastapi import Depends

from db.connection import get_connection_pool, AsyncConnectionPool
from db.dao import PostgreSQLDAO
from db.interfaces import DAOInterface, SQLQueryBuilderInterface
from db.query_builder import SQLQueryBuilder

_dao_instance: Optional[DAOInterface] = None


async def get_connection_pool_dependency() -> AsyncConnectionPool:
    """
    Dependency that provides a database connection pool.

    Returns:
        Configured database connection pool
    """
    return await get_connection_pool()


async def get_database_dao(
        connection_pool: AsyncConnectionPool = Depends(get_connection_pool_dependency)
) -> DAOInterface:
    """
    Dependency that provides a SINGLE database DAO instance.
    All repositories will share the same DAO for transaction consistency.

    Args:
        connection_pool: PostgreSQL connection pool

    Returns:
        Shared Data Access Object for database operations
    """
    global _dao_instance

    if _dao_instance is None:
        _dao_instance = PostgreSQLDAO(connection_pool)

    return _dao_instance


def get_query_builder(table_name: str) -> SQLQueryBuilderInterface:
    """
    Dependency for getting SQL query builder for specific table

    Args:
        table_name: Database table name

    Returns:
        SQLQueryBuilder instance
    """
    return SQLQueryBuilder(table_name)
