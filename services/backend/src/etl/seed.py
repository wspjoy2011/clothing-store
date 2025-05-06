import asyncio
import os
from asyncio import WindowsSelectorEventLoopPolicy

from db.connection import get_connection_pool
from etl.extract_transform import ProductCSVTransformer
from etl.load_to_db import DatabaseSeeder
from settings.config import config


async def main():
    transformer = ProductCSVTransformer(
        styles_path=config.STYLES_CSV,
        images_path=config.IMAGES_CSV
    )
    etl_result = transformer.execute()

    pool = await get_connection_pool()
    seeder = DatabaseSeeder(pool, etl_result)
    await seeder.seed()


if __name__ == "__main__":
    if os.name == "nt":
        asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())

    asyncio.run(main())
