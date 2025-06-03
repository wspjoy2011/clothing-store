"""CLI command for synchronizing products from PostgreSQL to Elasticsearch."""

import asyncio
import sys
from typing import Optional

import click
from elasticsearch import AsyncElasticsearch
from psycopg_pool import AsyncConnectionPool

from db.connection import get_connection_pool
from etl.sync.extractors import PostgreSQLProductExtractor
from etl.sync.loaders import ElasticsearchProductLoader
from etl.sync.migrator import ProductDataMigrator
from etl.sync.exceptions import SyncException
from settings.config import config
from settings.logging_config import get_logger

logger = get_logger(__name__, "sync_command")


@click.command()
@click.option(
    "--batch-size",
    default=1000,
    help="Number of products to process in each batch",
    type=int
)
@click.option(
    "--force",
    is_flag=True,
    help="Force migration without confirmation prompt"
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be migrated without actually doing it"
)
def sync_products(batch_size: int, force: bool, dry_run: bool) -> None:
    """
    Synchronize products from PostgreSQL to Elasticsearch.

    This command extracts product display names from catalog_products table
    and loads them into Elasticsearch for autocomplete functionality.
    """
    click.echo("Product Synchronization Tool")
    click.echo("=" * 40)

    if dry_run:
        click.echo("DRY RUN MODE - No actual changes will be made")

    try:
        asyncio.run(_run_sync(batch_size, force, dry_run))
    except KeyboardInterrupt:
        click.echo("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        click.echo(f"\nSync failed: {e}")
        logger.error(f"Command execution failed: {e}")
        sys.exit(1)


async def _run_sync(batch_size: int, force: bool, dry_run: bool) -> None:
    """
    Execute the synchronization process.

    Args:
        batch_size: Number of products per batch
        force: Skip confirmation prompt
        dry_run: Only show what would be done
    """
    pg_pool = None
    es_client = None

    try:
        pg_pool, es_client = await _setup_connections()

        async with pg_pool.connection() as connection:
            extractor = PostgreSQLProductExtractor(connection)
            loader = ElasticsearchProductLoader(es_client, config.ELASTICSEARCH_PRODUCTS_INDEX)
            migrator = ProductDataMigrator(extractor, loader)

            total_count = await extractor.get_products_count()

            click.echo(f"Found {total_count} products to synchronize")
            click.echo(f"Batch size: {batch_size}")
            click.echo(f"Target index: {config.ELASTICSEARCH_PRODUCTS_INDEX}")

            if dry_run:
                click.echo("Dry run completed - no changes made")
                return

            if not force:
                if not click.confirm(
                    f"\nThis will CLEAR the existing index and load {total_count} products. Continue?"
                ):
                    click.echo("Operation cancelled")
                    return

            click.echo("\nChecking Elasticsearch health...")
            if not await loader.health_check():
                raise SyncException("Elasticsearch is not healthy")
            click.echo("Elasticsearch is healthy")

            click.echo(f"\nStarting migration...")
            await migrator.migrate_products(batch_size)

            click.echo("Product synchronization completed successfully!")

    except SyncException as e:
        click.echo(f"\nSync error: {e}")
        raise
    except Exception as e:
        click.echo(f"\nUnexpected error: {e}")
        raise
    finally:
        await _cleanup_connections(pg_pool, es_client)


async def _setup_connections():
    """
    Setup database and Elasticsearch connections.

    Returns:
        Tuple of (pg_pool, es_client)
    """
    click.echo("Setting up connections...")

    try:
        pg_pool = await get_connection_pool()
        click.echo("PostgreSQL pool connected")
    except Exception as e:
        raise SyncException(f"Failed to connect to PostgreSQL: {e}")

    try:
        es_client = AsyncElasticsearch(
            hosts=[config.ELASTICSEARCH_URL],
            http_auth=config.ELASTICSEARCH_AUTH,
            verify_certs=False,
            ssl_show_warn=False,
            request_timeout=30,
            retry_on_timeout=True,
            max_retries=3
        )

        await es_client.info()
        click.echo("Elasticsearch connected")

    except Exception as e:
        if pg_pool:
            await pg_pool.close()
        raise SyncException(f"Failed to connect to Elasticsearch: {e}")

    return pg_pool, es_client


async def _cleanup_connections(
    pg_pool: Optional[AsyncConnectionPool],
    es_client: Optional[AsyncElasticsearch]
) -> None:
    """
    Cleanup database connections.

    Args:
        pg_pool: PostgreSQL connection pool to close
        es_client: Elasticsearch client to close
    """
    click.echo("Cleaning up connections...")

    if pg_pool:
        try:
            await pg_pool.close()
            click.echo("PostgreSQL pool closed")
        except Exception as e:
            click.echo(f"Warning: Failed to close PostgreSQL pool: {e}")

    if es_client:
        try:
            await es_client.close()
            click.echo("Elasticsearch connection closed")
        except Exception as e:
            click.echo(f"Warning: Failed to close Elasticsearch connection: {e}")


if __name__ == "__main__":
    sync_products()
