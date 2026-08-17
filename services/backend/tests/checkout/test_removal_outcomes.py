from typing import Any, List, Optional

import psycopg
import pytest

from apps.checkout.exceptions.repositories import CartStorageError
from apps.checkout.repositories.cart_item import CartItemRepository

ITEM_ID = 5
CART_ID = 1


class FailingDAO:
    """DAO whose statements never reach the database"""

    async def execute(self, **kwargs: Any) -> None:
        """Fail the way psycopg does when the server is unreachable"""
        raise psycopg.OperationalError("connection to server failed")


class EmptyResultDAO:
    """DAO reporting that the statement matched no row"""

    def __init__(self):
        self.executed: List[str] = []

    async def execute(self, query: str = "", **kwargs: Any) -> None:
        """Record the statement and report no row"""
        self.executed.append(query)
        return None


class DeletingDAO:
    """DAO reporting that one row was removed"""

    async def execute(self, **kwargs: Any) -> dict:
        """Report the identifier the statement returned"""
        return {"id": ITEM_ID}


async def test_an_unreachable_database_is_not_reported_as_a_missing_item():
    """A storage failure is raised, so nobody can read it as "no such item\""""
    repository = CartItemRepository(FailingDAO(), query_builder=None)

    with pytest.raises(CartStorageError):
        await repository.remove_cart_item(ITEM_ID, CART_ID)


async def test_an_item_of_another_cart_is_reported_as_not_removed():
    """A statement that matched nothing answers False, without raising"""
    repository = CartItemRepository(EmptyResultDAO(), query_builder=None)

    assert await repository.remove_cart_item(ITEM_ID, CART_ID) is False


async def test_a_removed_item_is_reported_as_removed():
    """A statement that removed the row answers True"""
    repository = CartItemRepository(DeletingDAO(), query_builder=None)

    assert await repository.remove_cart_item(ITEM_ID, CART_ID) is True


async def test_the_storage_failure_carries_the_original_error_for_the_log():
    """The cause travels with the exception instead of reaching the client"""
    repository = CartItemRepository(FailingDAO(), query_builder=None)

    with pytest.raises(CartStorageError) as failure:
        await repository.remove_cart_item(ITEM_ID, CART_ID)

    assert isinstance(failure.value.original_error, psycopg.Error)
