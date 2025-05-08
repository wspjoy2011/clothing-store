from fastapi import Depends

from apps.catalog.interfaces.repositories import ProductRepositoryInterface
from apps.catalog.interfaces.services import CatalogServiceInterface
from apps.catalog.repositories.product import ProductRepository
from apps.catalog.services.catalog import CatalogService
from db.connection import get_connection_pool, AsyncConnectionPool


async def get_connection_pool_dependency() -> AsyncConnectionPool:
    return await get_connection_pool()


async def get_product_repository(
        connection_pool: AsyncConnectionPool = Depends(get_connection_pool_dependency),
) -> ProductRepositoryInterface:
    return ProductRepository(connection_pool)


async def get_catalog_service(
        product_repository: ProductRepositoryInterface = Depends(get_product_repository),
) -> CatalogServiceInterface:
    return CatalogService(product_repository)
