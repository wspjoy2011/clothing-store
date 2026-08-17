from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, List, Optional, Tuple

UNSET = object()


class CommitFailed(Exception):
    """Raised by a fake connection when its transaction fails to commit"""


class FakeCursor:
    """Cursor returning preloaded rows and recording executed statements

    rowcount mirrors psycopg: it reports how many rows the statement affected,
    which is -1 until a statement has run.
    """

    def __init__(self, connection: "FakeConnection", row_factory: Optional[Any]):
        self._connection = connection
        self.row_factory = row_factory
        self.description: Optional[List[Tuple[str, ...]]] = connection.description
        self.rowcount: int = -1

    async def __aenter__(self) -> "FakeCursor":
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> bool:
        return False

    async def execute(self, query: str, params: Optional[List[Any]] = None) -> None:
        """Record the executed statement on the owning connection"""
        self._connection.executed.append((query, params))
        self.rowcount = self._connection.rowcount

    async def fetchone(self) -> Optional[Any]:
        """Return the first preloaded row"""
        return self._connection.rows[0] if self._connection.rows else None

    async def fetchall(self) -> List[Any]:
        """Return all preloaded rows"""
        return list(self._connection.rows)


class FakeTransaction:
    """Transaction recording its outcome on the owning connection"""

    def __init__(self, connection: "FakeConnection"):
        self._connection = connection

    async def __aenter__(self) -> "FakeTransaction":
        self._connection.events.append("BEGIN")
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> bool:
        if exc_type is not None:
            self._connection.events.append("ROLLBACK")
            return False

        if self._connection.fail_on_commit:
            raise CommitFailed(f"commit failed on {self._connection.name}")

        self._connection.events.append("COMMIT")
        return False


class FakeConnection:
    """Connection recording transaction events and executed statements"""

    def __init__(
            self,
            name: str,
            rows: Optional[List[Any]] = None,
            description: Any = UNSET,
            fail_on_commit: bool = False,
            rowcount: int = 0
    ):
        self.name = name
        self.rows = rows if rows is not None else []
        self.rowcount = rowcount
        self.description = [("column",)] if description is UNSET else description
        self.fail_on_commit = fail_on_commit
        self._isolation_level = None
        self.events: List[str] = []
        self.executed: List[Tuple[str, Optional[List[Any]]]] = []
        self.returned_to_pool = False

    @property
    def isolation_level(self) -> Optional[Any]:
        """Report the isolation level, read-only as on a real async connection"""
        return self._isolation_level

    async def set_isolation_level(self, value: Optional[Any]) -> None:
        """
        Change the isolation level the way an async connection requires

        Args:
            value: Level to apply, or None to restore the server default
        """
        self._isolation_level = value

    def transaction(self) -> FakeTransaction:
        """Start a fake transaction bound to this connection"""
        return FakeTransaction(self)

    def cursor(self, row_factory: Optional[Any] = None) -> FakeCursor:
        """Open a fake cursor bound to this connection"""
        return FakeCursor(self, row_factory)


class _ConnectionContext:
    """Async context manager handing out a connection and returning it to the pool"""

    def __init__(self, pool: "FakeConnectionPool"):
        self._pool = pool
        self._connection: Optional[FakeConnection] = None

    async def __aenter__(self) -> FakeConnection:
        self._connection = self._pool.acquire()
        return self._connection

    async def __aexit__(self, exc_type, exc_value, traceback) -> bool:
        self._pool.release(self._connection)
        return False


class FakeConnectionPool:
    """Connection pool reusing idle connections the way a real pool does

    A new connection is created only while every existing one is checked out.
    Reusing the same object matters: state left on a connection by one caller
    stays visible to the next one, which is exactly how state leaks between
    requests in production.
    """

    def __init__(
            self,
            rows: Optional[List[Any]] = None,
            description: Any = UNSET,
            fail_on_commit: bool = False,
            rowcount: int = 0
    ):
        self.rows = rows
        self.description = description
        self.fail_on_commit = fail_on_commit
        self.rowcount = rowcount
        self.created: List[FakeConnection] = []
        self.idle: List[FakeConnection] = []

    def acquire(self) -> FakeConnection:
        """
        Check out an idle connection, creating one only when none is free

        Returns:
            Connection handed to the caller
        """
        if self.idle:
            connection = self.idle.pop()
            connection.returned_to_pool = False
            return connection

        connection = FakeConnection(
            name=f"conn#{len(self.created) + 1}",
            rows=self.rows,
            description=self.description,
            fail_on_commit=self.fail_on_commit,
            rowcount=self.rowcount
        )
        self.created.append(connection)
        return connection

    def release(self, connection: FakeConnection) -> None:
        """
        Return a connection to the pool without resetting its state

        Args:
            connection: Connection being handed back
        """
        connection.returned_to_pool = True
        self.idle.append(connection)

    def connection(self) -> _ConnectionContext:
        """Acquire a connection as an async context manager"""
        return _ConnectionContext(self)

class FakeTransactionManager:
    """Transaction manager exposing an active transaction without a database"""

    def __init__(self):
        self.entered = 0
        self.committed = 0
        self.rolled_back = 0

    @asynccontextmanager
    async def atomic(self, isolation_level: Optional[Any] = None) -> AsyncIterator[None]:
        """
        Mark a transaction as active for the duration of the block

        Args:
            isolation_level: Accepted for interface compatibility

        Yields:
            Control to the wrapped block
        """
        from db.transaction import _current_transaction, TransactionState

        self.entered += 1
        token = _current_transaction.set(TransactionState(connection=FakeConnection("tx")))
        try:
            yield
        except Exception:
            self.rolled_back += 1
            raise
        else:
            self.committed += 1
        finally:
            _current_transaction.reset(token)

