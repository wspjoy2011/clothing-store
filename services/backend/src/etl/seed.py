import asyncio
import os

from db.connection import get_connection_pool
from etl.extract_transform import ProductCSVTransformer
from etl.load_to_db import DatabaseSeeder
from settings.config import config
from settings.logging_config import get_logger

logger = get_logger(__name__, "elt")


async def main():
    transformer = ProductCSVTransformer(
        styles_path=config.STYLES_CSV,
        images_path=config.IMAGES_CSV
    )
    etl_result = transformer.execute()

    pool = await get_connection_pool()
    seeder = DatabaseSeeder(pool, etl_result)

    is_empty = await seeder.is_database_empty()
    if is_empty:
        logger.info("Database is empty. Starting the seeding process...")
        await seeder.seed()
    else:
        logger.info("Database is already populated. Skipping seeding process.")


if __name__ == "__main__":
    if os.name == "nt":
        from asyncio import WindowsSelectorEventLoopPolicy

        asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())

    asyncio.run(main())
