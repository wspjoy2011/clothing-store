from db.dao import PostgreSQLDAO
from db.transaction import TransactionManager
from tests.fakes import FakeConnectionPool

UPDATE = "UPDATE accounts_users SET is_active = %s WHERE id = %s"


async def test_a_write_reports_how_many_rows_it_changed():
    """The count comes back to the caller, who cannot infer it from success"""
    pool = FakeConnectionPool(rowcount=3)
    dao = PostgreSQLDAO(pool)

    affected = await dao.execute_write(UPDATE, [True, 1])

    assert affected == 3


async def test_a_write_matching_nothing_reports_zero():
    """A statement that matched no row succeeds and says so honestly"""
    pool = FakeConnectionPool(rowcount=0)
    dao = PostgreSQLDAO(pool)

    affected = await dao.execute_write(UPDATE, [True, 999])

    assert affected == 0


async def test_a_write_joins_the_active_transaction():
    """A write inside a transaction uses its connection instead of taking another"""
    pool = FakeConnectionPool(rowcount=1)
    dao = PostgreSQLDAO(pool)
    manager = TransactionManager(pool)

    async with manager.atomic():
        await dao.execute_write(UPDATE, [True, 1])

    assert len(pool.created) == 1
    assert pool.created[0].events == ["BEGIN", "COMMIT"]


async def test_a_write_outside_a_transaction_takes_its_own_connection():
    """Without a transaction the write borrows a connection and returns it"""
    pool = FakeConnectionPool(rowcount=1)
    dao = PostgreSQLDAO(pool)

    await dao.execute_write(UPDATE, [True, 1])

    assert len(pool.created) == 1
    assert pool.created[0].returned_to_pool is True
