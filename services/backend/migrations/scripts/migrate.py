"""Database migration system."""

import hashlib
from pathlib import Path
from typing import List, Optional, cast, LiteralString
from psycopg_pool import AsyncConnectionPool
from psycopg import AsyncConnection
from psycopg import sql

from settings.logging_config import get_logger

logger = get_logger(__name__, "migrations")


class DatabaseMigrator:
    """Database migration manager."""

    ADVISORY_LOCK_KEY = 8_142_537_190_004_211

    class OutOfOrderMigration(RuntimeError):
        """Raised when a migration would be applied after a later one"""

    class ChangedMigration(RuntimeError):
        """Raised when an applied migration file no longer matches its checksum"""

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
               checksum   VARCHAR(64),
               applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
           )
        """)
        await connection.execute(create_table_sql)
        await connection.execute(
            sql.SQL("ALTER TABLE schema_migrations ADD COLUMN IF NOT EXISTS checksum VARCHAR(64)")
        )
        logger.info("Migrations table ensured")

    @staticmethod
    def checksum_of(migration_file: Path) -> str:
        """
        Compute the checksum recorded alongside an applied migration

        Args:
            migration_file: File whose contents are hashed

        Returns:
            Hexadecimal digest of the file contents
        """
        return hashlib.sha256(migration_file.read_bytes()).hexdigest()

    async def take_lock(self, connection: AsyncConnection) -> None:
        """
        Hold the migration lock for this connection

        Two runners starting at once compute the same pending list, and the second
        one fails on the bookkeeping primary key or on a statement that is not
        idempotent. The lock makes the second wait instead.

        Args:
            connection: Connection that will apply the migrations
        """
        await connection.execute(
            sql.SQL("SELECT pg_advisory_lock(%s)"), (self.ADVISORY_LOCK_KEY,)
        )
        logger.info("Migration lock acquired")

    async def verify_applied_migrations(self, connection: AsyncConnection) -> None:
        """
        Check that applied migrations still match what was applied

        Args:
            connection: Connection to read the bookkeeping from

        Raises:
            ChangedMigration: If a recorded checksum no longer matches the file
        """
        cursor = await connection.execute(
            sql.SQL("SELECT version, checksum FROM schema_migrations WHERE checksum IS NOT NULL")
        )

        for version, recorded in await cursor.fetchall():
            migration_file = self._find_migration_file(version)
            if migration_file is None:
                continue

            current = self.checksum_of(migration_file)
            if current != recorded:
                raise self.ChangedMigration(
                    f"migration {version} changed after it was applied: "
                    f"recorded {recorded[:12]}, file {current[:12]}"
                )

    def verify_order(self, applied: List[str], pending: List[str]) -> None:
        """
        Refuse a pending migration that predates one already applied

        Args:
            applied: Versions already applied
            pending: Versions about to be applied

        Raises:
            OutOfOrderMigration: If a pending version is lower than the highest applied
        """
        if not applied or not pending:
            return

        highest_applied = max(applied)
        late_arrivals = [version for version in pending if version < highest_applied]

        if late_arrivals:
            raise self.OutOfOrderMigration(
                f"migrations {late_arrivals} predate the applied {highest_applied}: "
                f"renumber them so the order on disk matches the order in the database"
            )

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

            insert_query = sql.SQL("INSERT INTO schema_migrations (version, checksum) VALUES (%s, %s)")
            await connection.execute(insert_query, (version, self.checksum_of(migration_file)))

        logger.info(f"Migration {version} applied successfully")

    def _find_migration_file(self, version: str) -> Optional[Path]:
        """Find migration file by version."""
        for file_path in self._migrations_dir.glob(f"{version}_*.sql"):
            return file_path
        return None

    async def migrate_to_latest(self) -> None:
        """Apply all pending migrations."""
        async with self._connection_pool.connection() as connection:
            await self.take_lock(connection)
            await self.ensure_migrations_table(connection)
            await self.verify_applied_migrations(connection)

            applied_migrations = await self.get_applied_migrations(connection)
            available_migrations = self.get_available_migrations()
            pending_migrations = self.get_pending_migrations(applied_migrations, available_migrations)
            self.verify_order(applied_migrations, pending_migrations)

            if not pending_migrations:
                logger.info("No pending migrations found")
                return

            logger.info(f"Found {len(pending_migrations)} pending migrations: {pending_migrations}")

            for version in pending_migrations:
                await self.apply_migration(connection, version)

            logger.info("All migrations applied successfully")

    async def get_migration_status(self) -> dict:
        """
        Get current migration status

        The integrity of applied migrations is checked here too: a status that
        reports "up to date" while a file has been edited since it was applied is
        the misleading answer this check exists to prevent.

        Returns:
            Applied, available and pending versions with their counts

        Raises:
            ChangedMigration: If an applied migration file no longer matches
        """
        async with self._connection_pool.connection() as connection:
            await self.ensure_migrations_table(connection)
            await self.verify_applied_migrations(connection)

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
