import asyncio

import pytest
from psycopg import IsolationLevel

from db.transaction import TransactionManager, get_current_transaction
from tests.fakes import CommitFailed, FakeConnection, FakeConnectionPool


async def test_transaction_commits_when_block_succeeds(connection_pool: FakeConnectionPool):
    """A block that returns normally commits its transaction"""
    manager = TransactionManager(connection_pool)

    async with manager.atomic():
        pass

    connection = connection_pool.created[0]
    assert connection.events == ["BEGIN", "COMMIT"]
    assert connection.returned_to_pool is True


async def test_transaction_rolls_back_when_block_raises(connection_pool: FakeConnectionPool):
    """A block that raises rolls back and lets the error reach the caller"""
    manager = TransactionManager(connection_pool)

    with pytest.raises(ValueError, match="business rule"):
        async with manager.atomic():
            raise ValueError("business rule")

    connection = connection_pool.created[0]
    assert connection.events == ["BEGIN", "ROLLBACK"]
    assert connection.returned_to_pool is True


async def test_commit_failure_reaches_the_caller():
    """A failing commit raises instead of being swallowed into the log"""
    pool = FakeConnectionPool(fail_on_commit=True)
    manager = TransactionManager(pool)

    with pytest.raises(CommitFailed):
        async with manager.atomic():
            pass

    assert pool.created[0].events == ["BEGIN"]


async def test_concurrent_transactions_never_share_a_connection(connection_pool: FakeConnectionPool):
    """Transactions running in parallel tasks each get their own connection"""
    manager = TransactionManager(connection_pool)

    async def run_transaction(hold: float) -> FakeConnection:
        async with manager.atomic():
            entered = get_current_transaction().connection
            await asyncio.sleep(hold)
            assert get_current_transaction().connection is entered
            return entered

    first, second = await asyncio.gather(run_transaction(0.05), run_transaction(0.01))

    assert first is not second
    assert len(connection_pool.created) == 2
    assert first.events == ["BEGIN", "COMMIT"]
    assert second.events == ["BEGIN", "COMMIT"]


async def test_failing_transaction_does_not_affect_a_parallel_one(connection_pool: FakeConnectionPool):
    """One task rolling back leaves a task running in parallel committed"""
    manager = TransactionManager(connection_pool)

    async def succeeding() -> None:
        async with manager.atomic():
            await asyncio.sleep(0.05)

    async def failing() -> None:
        async with manager.atomic():
            await asyncio.sleep(0.01)
            raise RuntimeError("boom")

    results = await asyncio.gather(succeeding(), failing(), return_exceptions=True)

    assert isinstance(results[1], RuntimeError)
    outcomes = sorted(connection.events[-1] for connection in connection_pool.created)
    assert outcomes == ["COMMIT", "ROLLBACK"]


async def test_nested_atomic_joins_the_outer_transaction(connection_pool: FakeConnectionPool):
    """A nested atomic block reuses the connection of the outer transaction"""
    manager = TransactionManager(connection_pool)

    async with manager.atomic():
        outer = get_current_transaction().connection
        async with manager.atomic():
            assert get_current_transaction().connection is outer

    assert len(connection_pool.created) == 1
    assert connection_pool.created[0].events == ["BEGIN", "COMMIT"]


async def test_transaction_state_is_cleared_after_the_block(connection_pool: FakeConnectionPool):
    """The active transaction is unset once the block exits"""
    manager = TransactionManager(connection_pool)

    assert get_current_transaction() is None
    async with manager.atomic():
        assert get_current_transaction() is not None
    assert get_current_transaction() is None


async def test_transaction_state_is_cleared_after_a_failure(connection_pool: FakeConnectionPool):
    """The active transaction is unset even when the block raises"""
    manager = TransactionManager(connection_pool)

    with pytest.raises(ValueError):
        async with manager.atomic():
            raise ValueError("boom")

    assert get_current_transaction() is None


async def test_isolation_level_is_applied_to_the_connection(connection_pool: FakeConnectionPool):
    """The requested isolation level is set on the transaction connection"""
    manager = TransactionManager(connection_pool)

    async with manager.atomic(isolation_level=IsolationLevel.SERIALIZABLE):
        pass

    assert connection_pool.created[0].isolation_level == IsolationLevel.SERIALIZABLE
