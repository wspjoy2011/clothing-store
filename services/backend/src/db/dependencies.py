from fastapi import Depends

from db.connection import get_connection_pool, AsyncConnectionPool
from db.dao import PostgreSQLDAO
from db.interfaces import DAOInterface


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
