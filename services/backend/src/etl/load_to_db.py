from async_lru import alru_cache
from psycopg_pool import AsyncConnectionPool
from tqdm.asyncio import tqdm_asyncio

from settings.logging_config import get_logger
from etl.models.dto import ETLResultDTO

logger = get_logger(__name__, "elt")


class DatabaseSeeder:
    def __init__(self, pool: AsyncConnectionPool, dto: ETLResultDTO):
        self._pool = pool
        self._dto = dto

    async def seed(self):
        """Public method to seed all tables."""
        logger.info("Starting database seeding...")
        async with self._pool.connection() as conn:
            await self._seed_master_categories(conn)
            await self._seed_sub_categories(conn)
            await self._seed_article_types(conn)
            await self._seed_base_colours(conn)
            await self._seed_seasons(conn)
            await self._seed_usage_types(conn)
            await self._seed_products(conn)
        logger.info("Database seeding completed successfully.")

    async def _seed_master_categories(self, conn):
        query = "INSERT INTO master_category (name) VALUES (%s) ON CONFLICT DO NOTHING;"
        for category in tqdm_asyncio(self._dto.master_categories, desc="Master Categories"):
            await conn.execute(query, (category.name,))

    async def _seed_sub_categories(self, conn):
        query = """
                INSERT INTO sub_category (master_category_id, name)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING; \
                """
        for sub_category in tqdm_asyncio(self._dto.sub_categories, desc="Sub Categories"):
            master_id = await self._get_master_category_id(conn, sub_category.master_category)
            await conn.execute(query, (master_id, sub_category.name))

    async def _seed_article_types(self, conn):
        query = """
                INSERT INTO article_type (sub_category_id, name)
                VALUES (%s, %s)
                ON CONFLICT DO NOTHING; \
                """
        for article_type in tqdm_asyncio(self._dto.article_types, desc="Article Types"):
            sub_cat_id = await self._get_sub_category_id(conn, article_type.sub_category)
            await conn.execute(query, (sub_cat_id, article_type.name))

    async def _seed_base_colours(self, conn):
        query = "INSERT INTO base_colour (name) VALUES (%s) ON CONFLICT DO NOTHING;"
        for colour in tqdm_asyncio(self._dto.base_colours, desc="Base Colours"):
            await conn.execute(query, (colour.name,))

    async def _seed_seasons(self, conn):
        query = "INSERT INTO season (name) VALUES (%s) ON CONFLICT DO NOTHING;"
        for season in tqdm_asyncio(self._dto.seasons, desc="Seasons"):
            await conn.execute(query, (season.name,))

    async def _seed_usage_types(self, conn):
        query = "INSERT INTO usage_type (name) VALUES (%s) ON CONFLICT DO NOTHING;"
        for usage in tqdm_asyncio(self._dto.usage_types, desc="Usage Types"):
            await conn.execute(query, (usage.name,))

    async def _seed_products(self, conn):
        query = """
                INSERT INTO products (product_id, gender, year, product_display_name, article_type_id,
                                      base_colour_id, season_id, usage_type_id, image_url)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (product_id) DO NOTHING; \
                """
        for product in tqdm_asyncio(self._dto.products, desc="Products"):
            article_type_id = await self._get_article_type_id(conn, product.article_type)
            base_colour_id = await self._get_base_colour_id(conn, product.base_colour)
            season_id = await self._get_season_id(conn, product.season)
            usage_type_id = await self._get_usage_type_id(conn, product.usage)

            await conn.execute(query, (
                product.product_id, product.gender, product.year,
                product.product_display_name, article_type_id,
                base_colour_id, season_id, usage_type_id,
                self._get_image_url_by_product_id(product.product_id)
            ))

    @alru_cache(maxsize=128)
    async def _get_master_category_id(self, conn, name: str) -> int:
        query = "SELECT master_category_id FROM master_category WHERE name=%s;"
        row = await conn.execute(query, (name,))
        result = await row.fetchone()
        return result[0]

    @alru_cache(maxsize=128)
    async def _get_sub_category_id(self, conn, name: str) -> int:
        query = "SELECT sub_category_id FROM sub_category WHERE name=%s;"
        row = await conn.execute(query, (name,))
        result = await row.fetchone()
        return result[0]

    @alru_cache(maxsize=128)
    async def _get_article_type_id(self, conn, name: str) -> int:
        query = "SELECT article_type_id FROM article_type WHERE name=%s;"
        row = await conn.execute(query, (name,))
        result = await row.fetchone()
        return result[0]

    @alru_cache(maxsize=128)
    async def _get_base_colour_id(self, conn, name: str) -> int:
        query = "SELECT base_colour_id FROM base_colour WHERE name=%s;"
        row = await conn.execute(query, (name,))
        result = await row.fetchone()
        return result[0]

    @alru_cache(maxsize=128)
    async def _get_season_id(self, conn, name: str) -> int:
        query = "SELECT season_id FROM season WHERE name=%s;"
        row = await conn.execute(query, (name,))
        result = await row.fetchone()
        return result[0]

    @alru_cache(maxsize=128)
    async def _get_usage_type_id(self, conn, name: str) -> int:
        query = "SELECT usage_type_id FROM usage_type WHERE name=%s;"
        row = await conn.execute(query, (name,))
        result = await row.fetchone()
        return result[0]

    def _get_image_url_by_product_id(self, product_id: int) -> str | None:
        """Get image URL by product_id."""
        for image in self._dto.images:
            if image.product_id == product_id:
                return image.image_url
        return None
