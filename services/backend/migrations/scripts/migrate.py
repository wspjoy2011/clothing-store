"""Database migration system."""

from pathlib import Path
from typing import List, Optional, cast, LiteralString
from psycopg_pool import AsyncConnectionPool
from psycopg import AsyncConnection
from psycopg import sql

from settings.logging_config import get_logger

logger = get_logger(__name__, "migrations")


class DatabaseMigrator:
    """Database migration manager."""

    def __init__(self, connection_pool: AsyncConnectionPool, migrations_dir: str):
        """
        Initialize migrator.

        Args:
            connection_pool: Database connection pool
            migrations_dir: Path to migrations directory (versions/up)
        """
        self._connection_pool = connection_pool
        self._migrations_dir = Path(migrations_dir)

    async def ensure_migrations_table(self, connection: AsyncConnection) -> None:
        """Create migrations table if it doesn't exist."""
        create_table_sql = sql.SQL("""
           CREATE TABLE IF NOT EXISTS schema_migrations (
               version    VARCHAR(255) PRIMARY KEY,
               applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
           )
        """)
        await connection.execute(create_table_sql)
        logger.info("Migrations table ensured")

    async def get_applied_migrations(self, connection: AsyncConnection) -> List[str]:
        """Get list of applied migration versions."""
        query = sql.SQL("SELECT version FROM schema_migrations ORDER BY version")
        cursor = await connection.execute(query)
        results = await cursor.fetchall()
        return [row[0] for row in results]

    def get_available_migrations(self) -> List[str]:
        """Get list of available migration files."""
        if not self._migrations_dir.exists():
            logger.warning(f"Migrations directory {self._migrations_dir} does not exist")
            return []

        migration_files = []
        for file_path in self._migrations_dir.glob("*.sql"):
            version = file_path.stem.split('_')[0]
            migration_files.append(version)

        return sorted(migration_files)

    def get_pending_migrations(self, applied: List[str], available: List[str]) -> List[str]:
        """Get list of migrations that need to be applied."""
        return [version for version in available if version not in applied]

    async def apply_migration(self, connection: AsyncConnection, version: str) -> None:
        """Apply a single migration."""
        migration_file = self._find_migration_file(version)
        if not migration_file:
            raise FileNotFoundError(f"Migration file for version {version} not found")

        logger.info(f"Applying migration {version}: {migration_file.name}")

        sql_content = sql.SQL(cast(LiteralString, migration_file.read_text(encoding='utf-8')))

        async with connection.transaction():
            await connection.execute(sql_content)

            insert_query = sql.SQL("INSERT INTO schema_migrations (version) VALUES (%s)")
            await connection.execute(insert_query, (version,))

        logger.info(f"Migration {version} applied successfully")

    def _find_migration_file(self, version: str) -> Optional[Path]:
        """Find migration file by version."""
        for file_path in self._migrations_dir.glob(f"{version}_*.sql"):
            return file_path
        return None

    async def migrate_to_latest(self) -> None:
        """Apply all pending migrations."""
        async with self._connection_pool.connection() as connection:
            await self.ensure_migrations_table(connection)

            applied_migrations = await self.get_applied_migrations(connection)
            available_migrations = self.get_available_migrations()
            pending_migrations = self.get_pending_migrations(applied_migrations, available_migrations)

            if not pending_migrations:
                logger.info("No pending migrations found")
                return

            logger.info(f"Found {len(pending_migrations)} pending migrations: {pending_migrations}")

            for version in pending_migrations:
                await self.apply_migration(connection, version)

            logger.info("All migrations applied successfully")

    async def get_migration_status(self) -> dict:
        """Get current migration status."""
        async with self._connection_pool.connection() as connection:
            await self.ensure_migrations_table(connection)

            applied_migrations = await self.get_applied_migrations(connection)
            available_migrations = self.get_available_migrations()
            pending_migrations = self.get_pending_migrations(applied_migrations, available_migrations)

            return {
                'applied': applied_migrations,
                'available': available_migrations,
                'pending': pending_migrations,
                'total_applied': len(applied_migrations),
                'total_pending': len(pending_migrations)
            }
