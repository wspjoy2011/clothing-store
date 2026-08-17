from fastapi import Depends

from apps.catalog.dependencies import get_catalog_service
from apps.catalog.interfaces.services import CatalogServiceInterface
from apps.checkout.interfaces import (
    CartItemRepositoryInterface,
    CartRepositoryInterface,
    CartServiceInterface,
    CartTokenRepositoryInterface,
)
from apps.checkout.repositories import CartItemRepository, CartRepository, CartTokenRepository
from apps.checkout.services import CartService
from db.dependencies import get_database_dao, get_query_builder, get_transaction_manager
from db.interfaces import DAOInterface, SQLQueryBuilderInterface, TransactionManagerInterface


async def get_cart_token_repository(
        dao: DAOInterface = Depends(get_database_dao),
        query_builder: SQLQueryBuilderInterface = Depends(lambda: get_query_builder("checkout_cart_tokens"))
) -> CartTokenRepositoryInterface:
    """
    Dependency for getting cart token repository.

    Args:
        dao: Data Access Object for database operations
        query_builder: SQL query builder for cart tokens table

    Returns:
        Initialized cart token repository
    """
    return CartTokenRepository(dao, query_builder)


async def get_cart_repository(
        dao: DAOInterface = Depends(get_database_dao),
        query_builder: SQLQueryBuilderInterface = Depends(lambda: get_query_builder("checkout_cart"))
) -> CartRepositoryInterface:
    """
    Dependency for getting cart repository.

    Args:
        dao: Data Access Object for database operations
        query_builder: SQL query builder for cart table

    Returns:
        Initialized cart repository
    """
    return CartRepository(dao, query_builder)


async def get_cart_item_repository(
        dao: DAOInterface = Depends(get_database_dao),
        query_builder: SQLQueryBuilderInterface = Depends(lambda: get_query_builder("checkout_cart_items"))
) -> CartItemRepositoryInterface:
    """
    Dependency for getting cart item repository.

    Args:
        dao: Data Access Object for database operations
        query_builder: SQL query builder for cart items table

    Returns:
        Initialized cart item repository
    """
    return CartItemRepository(dao, query_builder)


async def get_cart_service(
        cart_token_repository: CartTokenRepositoryInterface = Depends(get_cart_token_repository),
        cart_repository: CartRepositoryInterface = Depends(get_cart_repository),
        cart_item_repository: CartItemRepositoryInterface = Depends(get_cart_item_repository),
        catalog_service: CatalogServiceInterface = Depends(get_catalog_service),
        transaction_manager: TransactionManagerInterface = Depends(get_transaction_manager)
) -> CartServiceInterface:
    """
    Dependency for getting cart service.

    Args:
        cart_token_repository: Repository for cart token operations
        cart_repository: Repository for cart operations
        cart_item_repository: Repository for cart item operations
        catalog_service: Service for product information
        transaction_manager: Manager owning transaction boundaries

    Returns:
        Initialized cart service
    """
    return CartService(
        cart_token_repository=cart_token_repository,
        cart_repository=cart_repository,
        cart_item_repository=cart_item_repository,
        catalog_service=catalog_service,
        transaction_manager=transaction_manager
    )
