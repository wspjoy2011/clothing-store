"""CLI interface for database migrations."""

import asyncio
import sys
from pathlib import Path

import click

from db.connection import get_connection_pool
from migrations.scripts.migrate import DatabaseMigrator
from migrations.scripts.rollback import DatabaseRollbacker
from settings.logging_config import get_logger

logger = get_logger(__name__, "migrations_cli")


@click.group()
def cli():
    """Database migration commands."""
    click.echo("🗃️  Database Migration System")


@cli.command()
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show pending migrations without applying them"
)
@click.option(
    "--force",
    is_flag=True,
    help="Apply migrations without confirmation prompt"
)
def migrate(dry_run: bool, force: bool) -> None:
    """Apply pending database migrations."""
    if dry_run:
        click.echo("🔍 Migration Dry Run Mode")
    elif force:
        click.echo("⚡ Applying Database Migrations (Force Mode)")
    else:
        click.echo("⚡ Applying Database Migrations")

    click.echo("=" * 40)

    try:
        asyncio.run(_run_migrate(dry_run, force))
    except KeyboardInterrupt:
        click.echo("\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        click.echo(f"\n❌ Migration failed: {e}")
        logger.error(f"Migration command failed: {e}")
        sys.exit(1)


@cli.command()
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be rolled back without doing it"
)
@click.option(
    "--force",
    is_flag=True,
    help="Rollback without confirmation prompt"
)
@click.option(
    "--to-version",
    help="Rollback to specific version (exclusive)"
)
def rollback(dry_run: bool, force: bool, to_version: str) -> None:
    """Rollback database migrations."""
    if dry_run:
        click.echo("🔍 Rollback Dry Run Mode")
    elif force:
        click.echo("🔄 Rolling Back Database Migrations (Force Mode)")
    else:
        click.echo("🔄 Rolling Back Database Migrations")

    click.echo("=" * 40)

    try:
        asyncio.run(_run_rollback(dry_run, force, to_version))
    except KeyboardInterrupt:
        click.echo("\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        click.echo(f"\n❌ Rollback failed: {e}")
        logger.error(f"Rollback command failed: {e}")
        sys.exit(1)


@cli.command()
def status() -> None:
    """Show detailed migration status."""
    click.echo("📊 Migration Status")
    click.echo("=" * 25)

    try:
        asyncio.run(_show_status())
    except Exception as e:
        click.echo(f"\n❌ Failed to get status: {e}")
        logger.error(f"Status command failed: {e}")
        sys.exit(1)


async def _run_migrate(dry_run: bool, force: bool) -> None:
    """Execute migration process."""
    connection_pool = None

    try:
        click.echo("🔌 Connecting to database...")
        connection_pool = await get_connection_pool()
        click.echo("✅ Database connected")

        migrations_dir = Path(__file__).parent / "versions" / "up"
        migrator = DatabaseMigrator(connection_pool, str(migrations_dir))

        click.echo("📋 Checking migration status...")
        status = await migrator.get_migration_status()

        click.echo(f"📈 Applied migrations: {status['total_applied']}")
        click.echo(f"⏳ Pending migrations: {status['total_pending']}")

        if status['pending']:
            click.echo(f"📝 Pending versions: {', '.join(status['pending'])}")
        else:
            click.echo("✅ No pending migrations - database is up to date!")
            return

        if dry_run:
            click.echo("\n🔍 Dry run completed - no changes made")
            click.echo("💡 Run without --dry-run to apply these migrations")
            return

        if not force:
            if not click.confirm(f"\n🚀 Apply {status['total_pending']} pending migrations?"):
                click.echo("❌ Operation cancelled")
                return
        else:
            click.echo(f"\n🚀 Force applying {status['total_pending']} pending migrations...")

        click.echo(f"\n⚡ Applying {status['total_pending']} migrations...")

        with click.progressbar(length=status['total_pending'], label='Migrating') as bar:
            original_apply = migrator.apply_migration

            async def progress_apply(connection, version):
                await original_apply(connection, version)
                bar.update(1)

            migrator.apply_migration = progress_apply
            await migrator.migrate_to_latest()

        click.echo("✅ All migrations applied successfully!")

    except Exception as e:
        click.echo(f"\n❌ Migration error: {e}")
        raise
    finally:
        if connection_pool:
            click.echo("🔌 Closing database connection...")
            await connection_pool.close()


async def _run_rollback(dry_run: bool, force: bool, to_version: str) -> None:
    """Execute rollback process."""
    connection_pool = None

    try:
        click.echo("🔌 Connecting to database...")
        connection_pool = await get_connection_pool()
        click.echo("✅ Database connected")

        rollbacks_dir = Path(__file__).parent / "versions" / "down"
        rollbacker = DatabaseRollbacker(connection_pool, str(rollbacks_dir))

        click.echo("📋 Checking rollback status...")
        status = await rollbacker.get_rollback_status()

        click.echo(f"📈 Applied migrations: {status['total_applied']}")
        click.echo(f"🔄 Rollbackable migrations: {status['total_rollbackable']}")

        if status['latest_migration']:
            click.echo(f"🏷️  Latest migration: {status['latest_migration']}")

        if not status['rollbackable']:
            click.echo("✅ No migrations to rollback!")
            return

        if to_version:
            migrations_to_rollback = [v for v in status['rollbackable'] if v > to_version]
            if not migrations_to_rollback:
                click.echo(f"✅ Already at or before version {to_version}")
                return

            click.echo(f"📝 Will rollback to version {to_version}")
            click.echo(f"🔄 Migrations to rollback: {', '.join(migrations_to_rollback)}")

            if dry_run:
                click.echo("\n🔍 Dry run completed - no changes made")
                return

            if not force:
                if not click.confirm(f"\n🚀 Rollback {len(migrations_to_rollback)} migrations to version {to_version}?"):
                    click.echo("❌ Operation cancelled")
                    return
            else:
                click.echo(f"\n🚀 Force rolling back to version {to_version}...")

            click.echo(f"\n🔄 Rolling back {len(migrations_to_rollback)} migrations...")
            await rollbacker.rollback_to_version(to_version)
        else:
            click.echo(f"🔄 Will rollback latest migration: {status['latest_migration']}")

            if dry_run:
                click.echo("\n🔍 Dry run completed - no changes made")
                return

            if not force:
                if not click.confirm(f"\n🚀 Rollback latest migration ({status['latest_migration']})?"):
                    click.echo("❌ Operation cancelled")
                    return
            else:
                click.echo(f"\n🚀 Force rolling back latest migration...")

            click.echo(f"\n🔄 Rolling back migration {status['latest_migration']}...")
            await rollbacker.rollback_last_migration()

        click.echo("✅ Rollback completed successfully!")

    except Exception as e:
        click.echo(f"\n❌ Rollback error: {e}")
        raise
    finally:
        if connection_pool:
            click.echo("🔌 Closing database connection...")
            await connection_pool.close()


async def _show_status() -> None:
    """Show detailed migration status."""
    connection_pool = None

    try:
        click.echo("🔌 Connecting to database...")
        connection_pool = await get_connection_pool()
        click.echo("✅ Database connected")

        migrations_dir = Path(__file__).parent / "versions" / "up"
        rollbacks_dir = Path(__file__).parent / "versions" / "down"

        migrator = DatabaseMigrator(connection_pool, str(migrations_dir))
        rollbacker = DatabaseRollbacker(connection_pool, str(rollbacks_dir))

        click.echo("📊 Gathering migration status...")
        migrate_status = await migrator.get_migration_status()
        rollback_status = await rollbacker.get_rollback_status()

        click.echo(f"\n📈 Total available migrations: {len(migrate_status['available'])}")
        click.echo(f"✅ Applied migrations: {migrate_status['total_applied']}")
        click.echo(f"⏳ Pending migrations: {migrate_status['total_pending']}")
        click.echo(f"🔄 Rollbackable migrations: {rollback_status['total_rollbackable']}")

        click.echo(f"📁 Migrations directory: {migrations_dir}")
        click.echo(f"📁 Rollbacks directory: {rollbacks_dir}")

        click.echo()

        if migrate_status['applied']:
            click.echo("✅ Applied migrations:")
            for version in migrate_status['applied']:
                rollback_available = "🔄" if version in rollback_status['available_rollbacks'] else "❌"
                click.echo(f"  ✓ {version} {rollback_available}")

        if migrate_status['pending']:
            click.echo("\n⏳ Pending migrations:")
            for version in migrate_status['pending']:
                click.echo(f"  ○ {version}")

        if not migrate_status['available']:
            click.echo("⚠️  No migration files found")
            click.echo(f"💡 Add .sql files to: {migrations_dir}")

        click.echo()

        if migrate_status['pending']:
            click.echo("💡 Run 'migrate' command to apply pending migrations")
        elif rollback_status['rollbackable']:
            click.echo("💡 Run 'rollback' command to rollback migrations")
        else:
            click.echo("🎉 Database is up to date!")

        if rollback_status['latest_migration']:
            click.echo(f"🏷️  Latest migration: {rollback_status['latest_migration']}")

    except Exception as e:
        click.echo(f"❌ Status error: {e}")
        raise
    finally:
        if connection_pool:
            click.echo("🔌 Closing database connection...")
            await connection_pool.close()


if __name__ == "__main__":
    cli()
