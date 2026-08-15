import asyncio
from dataclasses import dataclass

from db.dao import PostgreSQLDAO
from db.transaction import TransactionManager
from tests.fakes import FakeConnectionPool


@dataclass
class Row:
    """Target class used to check model mapping"""

    column: str


async def test_execute_acquires_its_own_connection_outside_a_transaction(connection_pool: FakeConnectionPool):
    """Without an active transaction the DAO takes a connection from the pool"""
    dao = PostgreSQLDAO(connection_pool)

    await dao.execute("SELECT 1", [])

    assert len(connection_pool.created) == 1
    assert connection_pool.created[0].returned_to_pool is True


async def test_execute_runs_inside_the_active_transaction(connection_pool: FakeConnectionPool):
    """With an active transaction the DAO reuses its connection"""
    manager = TransactionManager(connection_pool)
    dao = PostgreSQLDAO(connection_pool)

    async with manager.atomic():
        await dao.execute("SELECT 1", [])
        await dao.execute("SELECT 2", [])

    assert len(connection_pool.created) == 1
    assert [query for query, _ in connection_pool.created[0].executed] == ["SELECT 1", "SELECT 2"]


async def test_queries_of_parallel_transactions_stay_on_their_own_connection(connection_pool: FakeConnectionPool):
    """Statements issued in parallel transactions never land on a foreign connection"""
    manager = TransactionManager(connection_pool)
    dao = PostgreSQLDAO(connection_pool)

    async def run_transaction(query: str, hold: float) -> None:
        async with manager.atomic():
            await asyncio.sleep(hold)
            await dao.execute(query, [])

    await asyncio.gather(run_transaction("SELECT 'a'", 0.05), run_transaction("SELECT 'b'", 0.01))

    executed = sorted(
        query
        for connection in connection_pool.created
        for query, _ in connection.executed
    )
    assert executed == ["SELECT 'a'", "SELECT 'b'"]
    assert all(len(connection.executed) == 1 for connection in connection_pool.created)


async def test_execute_passes_query_and_params():
    """Query text and parameters reach the cursor unchanged"""
    pool = FakeConnectionPool(rows=[("value",)])
    dao = PostgreSQLDAO(pool)

    await dao.execute("SELECT %s", ["value"])

    assert pool.created[0].executed == [("SELECT %s", ["value"])]


async def test_execute_defaults_missing_params_to_an_empty_list():
    """Omitted parameters are passed as an empty list"""
    pool = FakeConnectionPool(rows=[("value",)])
    dao = PostgreSQLDAO(pool)

    await dao.execute("SELECT 1")

    assert pool.created[0].executed == [("SELECT 1", [])]


async def test_execute_returns_a_single_row_when_asked():
    """fetch_one returns just the first row"""
    pool = FakeConnectionPool(rows=[("first",), ("second",)])
    dao = PostgreSQLDAO(pool)

    result = await dao.execute("SELECT 1", [], fetch_one=True)

    assert result == ("first",)


async def test_execute_returns_all_rows_by_default():
    """Without fetch_one every row is returned"""
    pool = FakeConnectionPool(rows=[("first",), ("second",)])
    dao = PostgreSQLDAO(pool)

    result = await dao.execute("SELECT 1", [])

    assert result == [("first",), ("second",)]


async def test_execute_returns_none_when_fetching_is_disabled():
    """fetch=False skips fetching entirely"""
    pool = FakeConnectionPool(rows=[("first",)])
    dao = PostgreSQLDAO(pool)

    result = await dao.execute("UPDATE t SET c = 1", [], fetch=False)

    assert result is None


async def test_execute_returns_none_for_statements_without_a_result_set():
    """A statement with no description returns None"""
    pool = FakeConnectionPool(rows=[], description=None)
    dao = PostgreSQLDAO(pool)

    result = await dao.execute("UPDATE t SET c = 1", [])

    assert result is None


async def test_execute_passes_the_model_class_as_row_factory():
    """model_class is turned into a psycopg row factory"""
    pool = FakeConnectionPool(rows=[Row(column="value")])
    dao = PostgreSQLDAO(pool)

    result = await dao.execute("SELECT 1", [], fetch_one=True, model_class=Row)

    assert result == Row(column="value")
