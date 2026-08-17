from typing import Any, List, Optional

import pytest

from apps.catalog.repositories.product import ProductRepository
from db.transaction import NoActiveTransactionError, TransactionManager
from tests.fakes import FakeConnectionPool

PRODUCT_ID = 10


class RecordingDAO:
    """DAO recording the statements it is asked to run"""

    def __init__(self, row: Optional[List[Any]] = None):
        self.row = row
        self.executed: List[str] = []

    async def execute(self, query: str, params: Optional[List[Any]] = None, **kwargs: Any) -> Optional[List[Any]]:
        """Record the statement and return the configured row"""
        self.executed.append(query)
        return self.row


def build_repository(row: Optional[List[Any]] = None) -> tuple:
    """
    Assemble a product repository over a recording DAO

    Args:
        row: Inventory row the DAO should return, or None for a missing product

    Returns:
        Repository and the DAO backing it
    """
    dao = RecordingDAO(row)
    return ProductRepository(dao=dao), dao


async def test_locking_outside_a_transaction_is_refused():
    """Outside a transaction the lock would be released at once, so it is refused"""
    repository, dao = build_repository([True, True, 5])

    with pytest.raises(NoActiveTransactionError):
        await repository.lock_inventory(PRODUCT_ID)

    assert dao.executed == []


async def test_locking_inside_a_transaction_reads_the_row_for_update():
    """Inside a transaction the row is read with a lock held until the end"""
    repository, dao = build_repository([True, True, 5])
    manager = TransactionManager(FakeConnectionPool())

    async with manager.atomic():
        inventory = await repository.lock_inventory(PRODUCT_ID)

    assert (inventory.is_active, inventory.is_in_stock, inventory.available_quantity) == (True, True, 5)
    assert "FOR UPDATE" in dao.executed[0]


async def test_a_product_without_inventory_reports_nothing():
    """A product with no inventory row yields no state to act on"""
    repository, _ = build_repository(None)
    manager = TransactionManager(FakeConnectionPool())

    async with manager.atomic():
        assert await repository.lock_inventory(PRODUCT_ID) is None
