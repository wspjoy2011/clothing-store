"""Database rollback system."""

from pathlib import Path
from typing import List, Optional, cast, LiteralString
from psycopg_pool import AsyncConnectionPool
from psycopg import AsyncConnection
from psycopg import sql

from settings.logging_config import get_logger

logger = get_logger(__name__, "rollbacks")


class DatabaseRollbacker:
    """Database rollback manager."""

    def __init__(self, connection_pool: AsyncConnectionPool, rollbacks_dir: str):
        """
        Initialize rollbacker.

        Args:
            connection_pool: Database connection pool
            rollbacks_dir: Path to rollbacks directory (versions/down)
        """
        self._connection_pool = connection_pool
        self._rollbacks_dir = Path(rollbacks_dir)

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
        """Get list of applied migration versions in reverse order (latest first)."""
        query = sql.SQL("SELECT version FROM schema_migrations ORDER BY version DESC")
        cursor = await connection.execute(query)
        results = await cursor.fetchall()
        return [row[0] for row in results]

    def get_available_rollbacks(self) -> List[str]:
        """Get list of available rollback files."""
        if not self._rollbacks_dir.exists():
            logger.warning(f"Rollbacks directory {self._rollbacks_dir} does not exist")
            return []

        rollback_files = []
        for file_path in self._rollbacks_dir.glob("*.sql"):
            version = file_path.stem.split('_')[0]
            rollback_files.append(version)

        return sorted(rollback_files, reverse=True)

    def get_rollbackable_migrations(self, applied: List[str], available_rollbacks: List[str]) -> List[str]:
        """Get list of migrations that can be rolled back."""
        return [version for version in applied if version in available_rollbacks]

    async def rollback_migration(self, connection: AsyncConnection, version: str) -> None:
        """Rollback a single migration."""
        rollback_file = self._find_rollback_file(version)
        if not rollback_file:
            raise FileNotFoundError(f"Rollback file for version {version} not found")

        logger.info(f"Rolling back migration {version}: {rollback_file.name}")

        sql_content = sql.SQL(cast(LiteralString, rollback_file.read_text(encoding='utf-8')))

        async with connection.transaction():
            await connection.execute(sql_content)

            delete_query = sql.SQL("DELETE FROM schema_migrations WHERE version = %s")
            await connection.execute(delete_query, (version,))

        logger.info(f"Migration {version} rolled back successfully")

    def _find_rollback_file(self, version: str) -> Optional[Path]:
        """Find rollback file by version."""
        for file_path in self._rollbacks_dir.glob(f"{version}_*.sql"):
            return file_path
        return None

    async def rollback_last_migration(self) -> None:
        """Rollback the last applied migration."""
        async with self._connection_pool.connection() as connection:
            await self.ensure_migrations_table(connection)

            applied_migrations = await self.get_applied_migrations(connection)
            available_rollbacks = self.get_available_rollbacks()
            rollbackable = self.get_rollbackable_migrations(applied_migrations, available_rollbacks)

            if not rollbackable:
                logger.info("No migrations to rollback")
                return

            latest_migration = rollbackable[0]
            logger.info(f"Rolling back latest migration: {latest_migration}")

            await self.rollback_migration(connection, latest_migration)
            logger.info("Latest migration rolled back successfully")

    async def rollback_to_version(self, target_version: str) -> None:
        """Rollback migrations to a specific version (exclusive)."""
        async with self._connection_pool.connection() as connection:
            await self.ensure_migrations_table(connection)

            applied_migrations = await self.get_applied_migrations(connection)
            available_rollbacks = self.get_available_rollbacks()
            rollbackable = self.get_rollbackable_migrations(applied_migrations, available_rollbacks)

            if not rollbackable:
                logger.info("No migrations to rollback")
                return

            migrations_to_rollback = []
            for version in rollbackable:
                if version > target_version:
                    migrations_to_rollback.append(version)
                else:
                    break

            if not migrations_to_rollback:
                logger.info(f"No migrations to rollback to version {target_version}")
                return

            logger.info(f"Rolling back {len(migrations_to_rollback)} migrations to version {target_version}")
            logger.info(f"Migrations to rollback: {migrations_to_rollback}")

            for version in migrations_to_rollback:
                await self.rollback_migration(connection, version)

            logger.info(f"Successfully rolled back to version {target_version}")

    async def get_rollback_status(self) -> dict:
        """Get current rollback status."""
        async with self._connection_pool.connection() as connection:
            await self.ensure_migrations_table(connection)

            applied_migrations = await self.get_applied_migrations(connection)
            available_rollbacks = self.get_available_rollbacks()
            rollbackable = self.get_rollbackable_migrations(applied_migrations, available_rollbacks)

            return {
                'applied': applied_migrations,
                'available_rollbacks': available_rollbacks,
                'rollbackable': rollbackable,
                'total_applied': len(applied_migrations),
                'total_rollbackable': len(rollbackable),
                'latest_migration': applied_migrations[0] if applied_migrations else None
            }
