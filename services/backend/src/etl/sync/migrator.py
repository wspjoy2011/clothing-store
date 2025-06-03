"""Data migration orchestrator for synchronizing products between PostgreSQL and Elasticsearch."""

import asyncio
from typing import List, Dict, Any

from etl.sync.interfaces import DataExtractorInterface, DataLoaderInterface, DataMigratorInterface
from etl.sync.exceptions import MigrationError
from settings.logging_config import get_logger

logger = get_logger(__name__, "data_migrator")


class ProductDataMigrator(DataMigratorInterface):
    """Orchestrates product data migration from PostgreSQL to Elasticsearch."""

    def __init__(
            self,
            extractor: DataExtractorInterface,
            loader: DataLoaderInterface
    ):
        """
        Initialize product data migrator.
        
        Args:
            extractor: Data extractor instance (PostgreSQL)
            loader: Data loader instance (Elasticsearch)
        """
        self._extractor = extractor
        self._loader = loader
        logger.info("Product data migrator initialized")

    async def migrate_products(self, batch_size: int = 1000) -> None:
        """
        Orchestrate full product data migration process.
        
        Steps:
        1. Health check for destination
        2. Create index if needed
        3. Get total products count
        4. Clear existing data
        5. Extract and load in batches
        6. Final verification
        
        Args:
            batch_size: Number of products to process in each batch
            
        Raises:
            MigrationError: When migration process fails
        """
        try:
            logger.info("Starting product data migration...")
            start_time = asyncio.get_event_loop().time()

            await self._perform_health_check()

            await self._ensure_index_exists()

            total_count = await self._get_total_products_count()

            await self._clear_destination()

            migrated_count = await self._extract_and_load_batches(batch_size, total_count)

            await self._verify_migration(total_count, migrated_count)

            end_time = asyncio.get_event_loop().time()
            duration = end_time - start_time

            logger.info(f"Migration completed successfully! "
                        f"Migrated {migrated_count}/{total_count} products in {duration:.2f}s")

        except Exception as e:
            logger.error(f"Migration failed: {e}")
            raise MigrationError(f"Product migration failed: {str(e)}", e)

    async def _perform_health_check(self) -> None:
        """
        Perform health check for destination system.
        
        Raises:
            MigrationError: When health check fails
        """
        logger.info("Performing destination health check...")

        is_healthy = await self._loader.health_check()
        if not is_healthy:
            raise MigrationError("Destination system is not healthy")

        logger.info("Destination health check passed")

    async def _ensure_index_exists(self) -> None:
        """
        Ensure destination index exists with proper mapping.
        
        Raises:
            MigrationError: When index creation fails
        """
        logger.info("Ensuring destination index exists...")

        try:
            await self._loader.create_index_if_not_exists()
            logger.info("Index verification completed")
        except Exception as e:
            raise MigrationError(f"Failed to ensure index exists: {str(e)}", e)

    async def _get_total_products_count(self) -> int:
        """
        Get total count of products to migrate.
        
        Returns:
            Total number of products
            
        Raises:
            MigrationError: When count query fails
        """
        logger.info("Getting total products count...")

        try:
            total_count = await self._extractor.get_products_count()
            logger.info(f"Total products to migrate: {total_count}")
            return total_count
        except Exception as e:
            raise MigrationError(f"Failed to get products count: {str(e)}", e)

    async def _clear_destination(self) -> None:
        """
        Clear existing data from destination.
        
        Raises:
            MigrationError: When clearing fails
        """
        logger.info("Clearing existing data from destination...")

        try:
            await self._loader.clear_index()
            logger.info("Destination cleared successfully")
        except Exception as e:
            raise MigrationError(f"Failed to clear destination: {str(e)}", e)

    async def _extract_and_load_batches(self, batch_size: int, total_count: int) -> int:
        """
        Extract and load products in batches.
        
        Args:
            batch_size: Size of each batch
            total_count: Total expected products count
            
        Returns:
            Number of successfully migrated products
            
        Raises:
            MigrationError: When batch processing fails
        """
        logger.info(f"Starting batch extraction and loading (batch_size={batch_size})...")

        migrated_count = 0
        batch_number = 0
        current_batch: List[Dict[str, Any]] = []

        try:
            async for product in self._extractor.extract_products():
                current_batch.append(product)

                if len(current_batch) >= batch_size:
                    batch_number += 1
                    await self._process_batch(current_batch, batch_number)
                    migrated_count += len(current_batch)

                    progress = (migrated_count / total_count) * 100 if total_count > 0 else 0
                    logger.info(f"Processed batch {batch_number}: {migrated_count}/{total_count} "
                                f"products ({progress:.1f}%)")

                    current_batch = []

            if current_batch:
                batch_number += 1
                await self._process_batch(current_batch, batch_number)
                migrated_count += len(current_batch)

                logger.info(f"Processed final batch {batch_number}: {migrated_count}/{total_count} products")

            return migrated_count

        except Exception as e:
            raise MigrationError(f"Batch processing failed at batch {batch_number}: {str(e)}", e)

    async def _process_batch(self, batch: List[Dict[str, Any]], batch_number: int) -> None:
        """
        Process a single batch of products.
        
        Args:
            batch: List of products to process
            batch_number: Current batch number for logging
            
        Raises:
            MigrationError: When batch processing fails
        """
        try:
            await self._loader.bulk_load_products(batch)
            logger.debug(f"Batch {batch_number} loaded successfully ({len(batch)} products)")
        except Exception as e:
            raise MigrationError(f"Failed to load batch {batch_number}: {str(e)}", e)

    async def _verify_migration(self, expected_count: int, actual_count: int) -> None:
        """
        Verify migration results.
        
        Args:
            expected_count: Expected number of products
            actual_count: Actually migrated products
            
        Raises:
            MigrationError: When counts don't match
        """
        logger.info(f"Verifying migration: expected={expected_count}, actual={actual_count}")

        if actual_count != expected_count:
            raise MigrationError(
                f"Migration count mismatch: expected {expected_count}, got {actual_count}"
            )

        logger.info("Migration verification passed")
