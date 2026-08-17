from fastapi import Depends

from db.connection import AsyncConnectionPool, get_connection_pool
from db.dao import PostgreSQLDAO
from db.interfaces import DAOInterface, SQLQueryBuilderInterface, TransactionManagerInterface
from db.query_builder import SQLQueryBuilder
from db.transaction import TransactionManager


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
    Dependency that provides a database DAO.

    Args:
        connection_pool: PostgreSQL connection pool

    Returns:
        Data Access Object for database operations
    """
    return PostgreSQLDAO(connection_pool)


async def get_transaction_manager(
        connection_pool: AsyncConnectionPool = Depends(get_connection_pool_dependency)
) -> TransactionManagerInterface:
    """
    Dependency that provides a transaction manager.

    Args:
        connection_pool: PostgreSQL connection pool

    Returns:
        Transaction manager owning transaction boundaries
    """
    return TransactionManager(connection_pool)


def get_query_builder(table_name: str) -> SQLQueryBuilderInterface:
    """
    Dependency for getting SQL query builder for specific table

    Args:
        table_name: Database table name

    Returns:
        SQLQueryBuilder instance
    """
    return SQLQueryBuilder(table_name)
