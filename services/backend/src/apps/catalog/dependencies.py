from fastapi import Depends

from apps.catalog.factories import (
    create_pagination_specification,
    create_ordering_specification,
    create_product_filter_specification
)
from apps.catalog.interfaces.repositories import ProductRepositoryInterface
from apps.catalog.interfaces.services import CatalogServiceInterface
from apps.catalog.repositories.product import ProductRepository
from apps.catalog.services.catalog import CatalogService
from db.dependencies import get_database_dao
from db.interfaces import DAOInterface


async def get_product_repository(
        dao: DAOInterface = Depends(get_database_dao),
) -> ProductRepositoryInterface:
    """
    Dependency for getting product repository.

    Args:
        dao: Data Access Object for database operations

    Returns:
        Initialized product repository
    """
    return ProductRepository(dao)


def get_pagination_specification_factory() -> callable:
    """
    Dependency for getting pagination specification factory.

    Returns:
        Function to create pagination specifications
    """
    return create_pagination_specification


def get_ordering_specification_factory() -> callable:
    """
    Dependency for getting ordering specification factory.

    Returns:
        Function to create ordering specifications
    """
    return create_ordering_specification


def get_filter_specification_factory() -> callable:
    """
    Dependency for getting filter specification factory.

    Returns:
        Function to create filter specifications
    """
    return create_product_filter_specification


async def get_catalog_service(
        product_repository: ProductRepositoryInterface = Depends(get_product_repository),
        pagination_specification_factory: callable = Depends(get_pagination_specification_factory),
        ordering_specification_factory: callable = Depends(get_ordering_specification_factory),
        filter_specification_factory: callable = Depends(get_filter_specification_factory),
) -> CatalogServiceInterface:
    """
    Dependency for getting catalog service.

    Args:
        product_repository: Repository for accessing product data
        pagination_specification_factory: Factory for creating pagination specifications
        ordering_specification_factory: Factory for creating ordering specifications
        filter_specification_factory: Factory for creating filter specifications

    Returns:
        Initialized catalog service
    """
    return CatalogService(
        product_repository=product_repository,
        pagination_specification_factory=pagination_specification_factory,
        ordering_specification_factory=ordering_specification_factory,
        filter_specification_factory=filter_specification_factory,
    )
