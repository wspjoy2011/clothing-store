import inspect

from apps.accounts.dependencies import get_registration_service
from db.dependencies import get_database_dao, get_transaction_manager
from db.interfaces import DAOInterface, TransactionManagerInterface
from tests.fakes import FakeConnectionPool


def test_application_exposes_versioned_routes():
    """The FastAPI application builds and mounts its routers"""
    from main import app

    paths = {route.path for route in app.routes}

    assert any(path.startswith("/api/v1/catalog") for path in paths)
    assert any(path.startswith("/api/v1/accounts") for path in paths)
    assert any(path.startswith("/api/v1/checkout") for path in paths)


async def test_dao_dependency_returns_the_declared_interface():
    """The DAO dependency provides an implementation of DAOInterface"""
    dao = await get_database_dao(FakeConnectionPool())

    assert isinstance(dao, DAOInterface)


async def test_transaction_manager_dependency_returns_the_declared_interface():
    """The transaction manager dependency provides an implementation of its interface"""
    manager = await get_transaction_manager(FakeConnectionPool())

    assert isinstance(manager, TransactionManagerInterface)


def test_registration_service_dependency_requires_a_transaction_manager():
    """The account service is wired with a transaction manager"""
    parameters = inspect.signature(get_registration_service).parameters

    assert "transaction_manager" in parameters
