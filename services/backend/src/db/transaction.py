from contextlib import asynccontextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from typing import AsyncIterator, Optional

from psycopg import AsyncConnection, IsolationLevel
from psycopg_pool import AsyncConnectionPool

from db.interfaces import TransactionManagerInterface
from settings.logging_config import get_logger

logger = get_logger(__name__, "db")


@dataclass(frozen=True)
class TransactionState:
    """Connection bound to the transaction currently active in this task"""

    connection: AsyncConnection


_current_transaction: ContextVar[Optional[TransactionState]] = ContextVar(
    "current_transaction",
    default=None
)


def get_current_transaction() -> Optional[TransactionState]:
    """
    Get the transaction active in the current asynchronous task

    Returns:
        Active transaction state, or None when running outside a transaction
    """
    return _current_transaction.get()


class TransactionManager(TransactionManagerInterface):
    """Transaction manager storing its state per asynchronous task"""

    def __init__(self, connection_pool: AsyncConnectionPool):
        self._connection_pool = connection_pool

    @asynccontextmanager
    async def atomic(
            self,
            isolation_level: Optional[IsolationLevel] = None
    ) -> AsyncIterator[None]:
        """
        Run the wrapped block in a single database transaction

        Args:
            isolation_level: Isolation level applied to the outermost transaction

        Yields:
            Control to the wrapped block
        """
        if _current_transaction.get() is not None:
            logger.debug("Joining transaction already active in this task")
            yield
            return

        async with self._connection_pool.connection() as connection:
            previous_isolation_level = connection.isolation_level

            try:
                if isolation_level is not None:
                    connection.isolation_level = isolation_level

                async with connection.transaction():
                    token = _current_transaction.set(TransactionState(connection=connection))
                    logger.debug("Transaction started")
                    try:
                        yield
                    finally:
                        _current_transaction.reset(token)
                        logger.debug("Transaction finished")
            finally:
                if isolation_level is not None:
                    connection.isolation_level = previous_isolation_level
