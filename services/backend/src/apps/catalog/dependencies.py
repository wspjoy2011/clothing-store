from fastapi import Depends

from apps.catalog.factories import SpecificationFactory
from apps.catalog.interfaces.factories import SpecificationFactoryInterface
from apps.catalog.interfaces.repositories import CategoryRepositoryInterface, ProductRepositoryInterface
from apps.catalog.interfaces.services import CatalogServiceInterface
from apps.catalog.repositories.category import CategoryRepository
from apps.catalog.repositories.product import ProductRepository
from apps.catalog.services.catalog import CatalogService
from db.dependencies import get_database_dao
from db.interfaces import DAOInterface
from search.dependencies import get_autocomplete_client
from search.interfaces import AutocompleteClientInterface


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







def get_specification_factory() -> SpecificationFactoryInterface:
    """
    Dependency for getting the specification factory

    Returns:
        Factory building the specifications of a catalogue query
    """
    return SpecificationFactory()


async def get_catalog_service(
        product_repository: ProductRepositoryInterface = Depends(get_product_repository),
        category_repository: CategoryRepositoryInterface = Depends(get_category_repository),
        specifications: SpecificationFactoryInterface = Depends(get_specification_factory),
        autocomplete_client: AutocompleteClientInterface = Depends(get_autocomplete_client),
) -> CatalogServiceInterface:
    """
    Dependency for getting catalog service.

    Args:
        product_repository: Repository for accessing product data
        category_repository: Repository for accessing category data
        specifications: Factory building the specifications of a query
        autocomplete_client: Autocomplete client for product suggestions

    Returns:
        Initialized catalog service
    """
    return CatalogService(
        product_repository=product_repository,
        category_repository=category_repository,
        specifications=specifications,
        autocomplete_client=autocomplete_client,
    )
