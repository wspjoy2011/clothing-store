from fastapi import Depends

from apps.catalog.factories import create_pagination_specification, create_ordering_specification
from apps.catalog.interfaces.repositories import ProductRepositoryInterface
from apps.catalog.interfaces.services import CatalogServiceInterface
from apps.catalog.interfaces.specifications import PaginationSpecificationInterface
from apps.catalog.repositories.product import ProductRepository
from apps.catalog.services.catalog import CatalogService
from apps.catalog.specifications.pagination import PaginationSpecification
from db.connection import get_connection_pool, AsyncConnectionPool


async def get_connection_pool_dependency() -> AsyncConnectionPool:
    return await get_connection_pool()


async def get_product_repository(
        connection_pool: AsyncConnectionPool = Depends(get_connection_pool_dependency),
) -> ProductRepositoryInterface:
    return ProductRepository(connection_pool)


def get_pagination_specification_factory() -> callable:
    return create_pagination_specification


def get_ordering_specification_factory() -> callable:
    return create_ordering_specification


async def get_catalog_service(
        product_repository: ProductRepositoryInterface = Depends(get_product_repository),
        pagination_specification_factory: callable = Depends(get_pagination_specification_factory),
        ordering_specification_factory: callable = Depends(get_ordering_specification_factory),
) -> CatalogServiceInterface:
    return CatalogService(
        product_repository=product_repository,
        pagination_specification_factory=pagination_specification_factory,
        ordering_specification_factory=ordering_specification_factory,
    )
