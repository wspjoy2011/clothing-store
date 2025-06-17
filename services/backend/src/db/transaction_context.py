from contextvars import ContextVar
from typing import Optional, List
from functools import wraps
import traceback

from db.interfaces import DAOInterface
from settings.logging_config import get_logger

logger = get_logger(__name__, "db")

_current_transaction: ContextVar[Optional['TransactionContext']] = ContextVar('current_transaction', default=None)


class TransactionContext:
    """Context for managing database transactions across multiple DAO calls"""

    def __init__(self, dao: DAOInterface):
        self._dao = dao
        self._connection = None
        self._transaction = None
        self._is_active = False

    async def __aenter__(self):
        """Start transaction context"""
        try:
            logger.debug("Starting transaction context...")

            await self._dao.begin_transaction()

            self._connection = self._dao._current_connection
            self._transaction = self._dao._current_transaction
            self._is_active = True

            _current_transaction.set(self)

            logger.info("Transaction context started successfully - BEGIN TRANSACTION executed")
            return self

        except Exception as e:
            logger.error(f"Failed to start transaction context: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """End transaction context"""
        try:
            if exc_type is None:
                await self._dao.commit_transaction()
                logger.info("Transaction committed successfully - COMMIT executed")
            else:
                await self._dao.rollback_transaction()
                logger.warning(f"Transaction rolled back - ROLLBACK executed due to: {exc_type.__name__}: {exc_val}")
                logger.debug(f"Full traceback: {traceback.format_exception(exc_type, exc_val, exc_tb)}")
        except Exception as commit_rollback_error:
            logger.error(f"Error during transaction cleanup: {commit_rollback_error}")
            logger.error(f"Cleanup traceback: {traceback.format_exc()}")
        finally:
            self._is_active = False
            _current_transaction.set(None)
            logger.debug("Transaction context cleaned up")

    def get_connection(self):
        """Get current transaction connection"""
        return self._connection if self._is_active else None


def atomic(repository_attrs: List[str], dao_attr_name: str = '_dao'):
    """
    Decorator that wraps method execution in database transaction.
    Validates that all repositories use the same DAO instance.

    Args:
        repository_attrs: List of repository attribute names that participate in transaction
        dao_attr_name: Name of DAO attribute in each repository (default: '_dao')

    Example:
        @atomic(['_user_repository', '_user_group_repository', '_token_repository'])
        async def register_user(self, user_data):
            # All repositories will use the same transaction
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                logger.debug(
                    f"@atomic decorator called for function: {func.__name__} with repositories: {repository_attrs}")

                current_tx = _current_transaction.get()
                if current_tx and current_tx._is_active:
                    logger.debug("Already in transaction, executing function directly")
                    return await func(*args, **kwargs)

                if not args:
                    logger.warning("No arguments provided to decorated function, executing without transaction")
                    return await func(*args, **kwargs)

                service_instance = args[0]
                daos = []

                for repo_attr in repository_attrs:
                    if not hasattr(service_instance, repo_attr):
                        logger.warning(
                            f"Repository attribute '{repo_attr}' not found in {type(service_instance).__name__}, executing without transaction")
                        return await func(*args, **kwargs)

                    repository = getattr(service_instance, repo_attr)

                    if not hasattr(repository, dao_attr_name):
                        logger.warning(
                            f"DAO attribute '{dao_attr_name}' not found in repository '{repo_attr}', executing without transaction")
                        return await func(*args, **kwargs)

                    dao = getattr(repository, dao_attr_name)
                    daos.append((repo_attr, dao))
                    logger.debug(f"Found DAO in repository '{repo_attr}': {type(dao).__name__}")

                if not daos:
                    logger.warning("No DAOs found in any repositories, executing without transaction")
                    return await func(*args, **kwargs)

                first_dao = daos[0][1]
                for repo_attr, dao in daos[1:]:
                    if dao is not first_dao:
                        logger.error(
                            f"DAO instance mismatch! Repository '{repo_attr}' uses different DAO instance than '{daos[0][0]}'")
                        logger.error("All repositories must share the same DAO instance for transaction consistency")
                        raise ValueError(
                            f"Repository '{repo_attr}' uses different DAO instance. Transaction integrity violation.")

                logger.info(f"All {len(daos)} repositories use the same DAO instance. Transaction integrity validated.")

                logger.debug("Creating new transaction context with shared DAO")
                async with TransactionContext(first_dao):
                    logger.debug(f"Executing {func.__name__} within transaction")
                    result = await func(*args, **kwargs)
                    logger.debug(f"Function {func.__name__} completed successfully")
                    return result

            except Exception as e:
                logger.error(f"Error in @atomic decorator for {func.__name__}: {e}")
                logger.error(f"Decorator traceback: {traceback.format_exc()}")
                raise

        return wrapper

    return decorator
