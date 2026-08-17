from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, List, Optional, Tuple

from psycopg import ProgrammingError
from psycopg.pq import ExecStatus

UNSET = object()
ENCODING = "utf-8"


class FakeResult:
    """Result description a psycopg row factory can read

    The real factories take column names from the result, not from the cursor
    description, so a fake that only carries a description cannot map anything
    and every mapping assertion above it would be vacuous.
    """

    def __init__(self, names: List[str]):
        self._names = [name.encode(ENCODING) for name in names]
        self.status = ExecStatus.TUPLES_OK

    @property
    def nfields(self) -> int:
        """Report how many columns the result carries"""
        return len(self._names)

    def fname(self, index: int) -> bytes:
        """
        Report the name of one column

        Args:
            index: Zero-based column position

        Returns:
            Column name as bytes, the way libpq hands it over
        """
        return self._names[index]


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
        self._encoding = ENCODING
        self.pgresult = FakeResult([column[0] for column in connection.description])             if connection.description else None

    async def __aenter__(self) -> "FakeCursor":
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> bool:
        return False

    async def execute(self, query: str, params: Optional[List[Any]] = None) -> None:
        """Record the executed statement on the owning connection"""
        self._connection.executed.append((query, params))
        self._connection.pending_work = True
        self.rowcount = self._connection.rowcount

    async def fetchone(self) -> Optional[Any]:
        """Return the first preloaded row, mapped the way the row factory asks"""
        if not self._connection.rows:
            return None
        return self._map(self._connection.rows[0])

    def _map(self, row: Any) -> Any:
        """
        Apply the row factory the way psycopg does

        The factory is what turns a raw row into a model or a dictionary. A fake
        that ignores it lets a test assert on a mapping nothing performed.

        Args:
            row: Raw row as stored on the connection

        Returns:
            Row mapped by the factory, or the raw row when there is none
        """
        if self.row_factory is None:
            return row

        maker = self.row_factory(self)
        return maker(row)

    async def fetchall(self) -> List[Any]:
        """Return all preloaded rows, mapped the way the row factory asks"""
        return [self._map(row) for row in self._connection.rows]


class FakeTransaction:
    """Transaction recording its outcome on the owning connection"""

    def __init__(self, connection: "FakeConnection"):
        self._connection = connection

    async def __aenter__(self) -> "FakeTransaction":
        self._connection.events.append("BEGIN")
        self._connection.in_transaction = True
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> bool:
        self._connection.in_transaction = False

        if exc_type is not None:
            self._connection.events.append("ROLLBACK")
            self._connection.pending_work = False
            return False

        if self._connection.fail_on_commit:
            raise CommitFailed(f"commit failed on {self._connection.name}")

        self._connection.events.append("COMMIT")
        self._connection.pending_work = False
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
        self.pending_work = False
        self.in_transaction = False
        self.returned_to_pool = False

    @property
    def isolation_level(self) -> Optional[Any]:
        """Report the isolation level, read-only as on a real async connection"""
        return self._isolation_level

    async def set_isolation_level(self, value: Optional[Any]) -> None:
        """
        Change the isolation level the way an async connection requires

        psycopg refuses this inside a transaction, so the fake refuses too: a fake
        that allows it would keep passing if the restore moved inside the block.

        Args:
            value: Level to apply, or None to restore the server default

        Raises:
            ProgrammingError: If a transaction is currently open
        """
        if self.in_transaction:
            raise ProgrammingError("the isolation level cannot be changed inside a transaction")

        self._isolation_level = value

    def transaction(self) -> FakeTransaction:
        """Start a fake transaction bound to this connection"""
        return FakeTransaction(self)

    def cursor(self, row_factory: Optional[Any] = None) -> FakeCursor:
        """Open a fake cursor bound to this connection"""
        return FakeCursor(self, row_factory)


class _ConnectionContext:
    """Async context manager handing out a connection and returning it to the pool

    Leaving the block commits on success and rolls back on failure, the way the
    real pool does by entering the connection as a context manager. Without it a
    write performed outside an explicit transaction would appear to be stored in a
    test while nothing committed it in production.
    """

    def __init__(self, pool: "FakeConnectionPool"):
        self._pool = pool
        self._connection: Optional[FakeConnection] = None

    async def __aenter__(self) -> FakeConnection:
        self._connection = self._pool.acquire()
        return self._connection

    async def __aexit__(self, exc_type, exc_value, traceback) -> bool:
        if self._connection.pending_work:
            self._connection.events.append("ROLLBACK" if exc_type is not None else "COMMIT")
            self._connection.pending_work = False

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
        self.isolation_levels: List[Optional[Any]] = []

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
        self.isolation_levels.append(isolation_level)
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

