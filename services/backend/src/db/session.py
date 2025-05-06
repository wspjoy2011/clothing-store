from typing import AsyncGenerator

from psycopg import AsyncConnection

from db.connection import get_connection_pool


async def get_postgresql_connection() -> AsyncGenerator[AsyncConnection, None]:
    """Provide an async database connection from the pool."""
    pool = await get_connection_pool()
    async with pool.connection() as connection:
        yield connection
