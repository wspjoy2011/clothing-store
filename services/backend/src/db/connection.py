import warnings

from psycopg_pool import AsyncConnectionPool

from settings.config import config

warnings.filterwarnings(
    "ignore",
    message="opening the async pool AsyncConnectionPool in the constructor is deprecated",
)

_pool: AsyncConnectionPool | None = None


def build_dsn() -> str:
    """Assemble DSN from environment‑driven AppConfig."""
    return (
        f"postgresql://{config.POSTGRES_USER}:{config.POSTGRES_PASSWORD}"
        f"@{config.POSTGRES_HOST}:{config.POSTGRES_DB_PORT}/{config.POSTGRES_DB}"
    )


async def get_connection_pool() -> AsyncConnectionPool:
    """Get or create an asynchronous PostgreSQL connection pool."""
    global _pool

    if _pool is None:
        _pool = AsyncConnectionPool(
            conninfo=build_dsn(),
            min_size=1,
            max_size=10,
            timeout=60,
        )
        await _pool.open()
        await _pool.wait()
    return _pool

