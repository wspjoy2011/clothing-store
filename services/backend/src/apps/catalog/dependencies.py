from fastapi import Depends

from apps.catalog.factories import (
    create_pagination_specification,
    create_ordering_specification,
    create_product_filter_specification,
    create_search_specification,
    create_category_specification
)
from apps.catalog.interfaces.repositories import (
    ProductRepositoryInterface,
    CategoryRepositoryInterface
)
from apps.catalog.interfaces.services import CatalogServiceInterface
from apps.catalog.repositories.category import CategoryRepository
from apps.catalog.repositories.product import ProductRepository
from apps.catalog.services.catalog import CatalogService
from db.dependencies import get_database_dao, get_query_builder
from db.interfaces import DAOInterface, SQLQueryBuilderInterface


async def get_product_repository(
        dao: DAOInterface = Depends(get_database_dao),
        query_builder: SQLQueryBuilderInterface = Depends(lambda: get_query_builder("catalog_products"))
) -> ProductRepositoryInterface:
    """
    Dependency for getting product repository.

    Args:
        dao: Data Access Object for database operations
        query_builder: SQL query builder for product table

    Returns:
        Initialized product repository
    """
    return ProductRepository(dao, query_builder)


async def get_category_repository(
        dao: DAOInterface = Depends(get_database_dao),
) -> CategoryRepositoryInterface:
    """
    Dependency for getting category repository.

    Args:
        dao: Data Access Object for database operations

    Returns:
        Initialized category repository
    """
    return CategoryRepository(dao)


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


def get_search_specification_factory() -> callable:
    """
    Get factory for creating search specifications

    Returns:
        Factory function for creating search specifications
    """
    return create_search_specification


def get_category_specification_factory() -> callable:
    """
    Dependency for getting category specification factory.

    Returns:
        Function to create category specifications
    """
    return create_category_specification


async def get_catalog_service(
        product_repository: ProductRepositoryInterface = Depends(get_product_repository),
        category_repository: CategoryRepositoryInterface = Depends(get_category_repository),
        pagination_specification_factory: callable = Depends(get_pagination_specification_factory),
        ordering_specification_factory: callable = Depends(get_ordering_specification_factory),
        filter_specification_factory: callable = Depends(get_filter_specification_factory),
        search_specification_factory: callable = Depends(get_search_specification_factory),
        category_specification_factory: callable = Depends(get_category_specification_factory),
) -> CatalogServiceInterface:
    """
    Dependency for getting catalog service.

    Args:
        product_repository: Repository for accessing product data
        category_repository: Repository for accessing category data
        pagination_specification_factory: Factory for creating pagination specifications
        ordering_specification_factory: Factory for creating ordering specifications
        filter_specification_factory: Factory for creating filter specifications
        search_specification_factory: Factory for creating search specifications
        category_specification_factory: Factory for creating category specifications

    Returns:
        Initialized catalog service
    """
    return CatalogService(
        product_repository=product_repository,
        category_repository=category_repository,
        pagination_specification_factory=pagination_specification_factory,
        ordering_specification_factory=ordering_specification_factory,
        filter_specification_factory=filter_specification_factory,
        search_specification_factory=search_specification_factory,
        category_specification_factory=category_specification_factory,
    )
