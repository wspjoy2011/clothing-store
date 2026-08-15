from typing import Any, List, Optional, Tuple

UNSET = object()


class CommitFailed(Exception):
    """Raised by a fake connection when its transaction fails to commit"""


class FakeCursor:
    """Cursor returning preloaded rows and recording executed statements"""

    def __init__(self, connection: "FakeConnection", row_factory: Optional[Any]):
        self._connection = connection
        self.row_factory = row_factory
        self.description: Optional[List[Tuple[str, ...]]] = connection.description

    async def __aenter__(self) -> "FakeCursor":
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> bool:
        return False

    async def execute(self, query: str, params: Optional[List[Any]] = None) -> None:
        """Record the executed statement on the owning connection"""
        self._connection.executed.append((query, params))

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
            fail_on_commit: bool = False
    ):
        self.name = name
        self.rows = rows if rows is not None else []
        self.description = [("column",)] if description is UNSET else description
        self.fail_on_commit = fail_on_commit
        self.isolation_level = None
        self.events: List[str] = []
        self.executed: List[Tuple[str, Optional[List[Any]]]] = []
        self.returned_to_pool = False

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
        self._connection = self._pool.create_connection()
        return self._connection

    async def __aexit__(self, exc_type, exc_value, traceback) -> bool:
        self._connection.returned_to_pool = True
        return False


class FakeConnectionPool:
    """Connection pool creating a new fake connection on every acquisition"""

    def __init__(
            self,
            rows: Optional[List[Any]] = None,
            description: Any = UNSET,
            fail_on_commit: bool = False
    ):
        self.rows = rows
        self.description = description
        self.fail_on_commit = fail_on_commit
        self.created: List[FakeConnection] = []

    def create_connection(self) -> FakeConnection:
        """Create and register a new fake connection"""
        connection = FakeConnection(
            name=f"conn#{len(self.created) + 1}",
            rows=self.rows,
            description=self.description,
            fail_on_commit=self.fail_on_commit
        )
        self.created.append(connection)
        return connection

    def connection(self) -> _ConnectionContext:
        """Acquire a connection as an async context manager"""
        return _ConnectionContext(self)
