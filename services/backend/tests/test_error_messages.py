import pytest
from fastapi.testclient import TestClient

from apps.accounts.dependencies import get_authentication_service, get_password_service, get_registration_service
from apps.accounts.services.exceptions import (
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    PasswordResetError,
    UserCreationError,
    UserNotFoundError,
)
from apps.checkout.dependencies import get_cart_service
from apps.checkout.exceptions import CartNotFoundError, CartTokenCreationError, InsufficientStockError
from main import app

INTERNAL_TEXT = (
    'connection to server at "10.0.0.7", port 5432 failed; '
    'constraint "accounts_users_email_key"; relation "accounts_users"; user_id=42'
)

FORBIDDEN_FRAGMENTS = [
    "10.0.0.7",
    "5432",
    "accounts_users",
    "constraint",
    "relation",
    "user_id=42",
    "psycopg",
    "Traceback",
]


class FailingAccountService:
    """Stand-in for any account service, failing every call with a technical message"""

    def __init__(self, error: Exception):
        self.error = error

    async def register_user(self, *args, **kwargs):
        """Fail the registration"""
        raise self.error

    async def login_user(self, *args, **kwargs):
        """Fail the login"""
        raise self.error

    async def request_password_reset(self, *args, **kwargs):
        """Fail the password reset request"""
        raise self.error


class FailingCartService:
    """Cart service failing every call with a technical message"""

    def __init__(self, error: Exception):
        self.error = error

    async def create_cart_token(self, *args, **kwargs):
        """Fail the token creation"""
        raise self.error

    async def get_or_create_cart_for_token(self, *args, **kwargs):
        """Fail the cart lookup"""
        raise self.error

    async def add_item_to_cart(self, *args, **kwargs):
        """Fail adding to the cart"""
        raise self.error


def assert_no_internals(body: str) -> None:
    """
    Assert the response body carries nothing from inside the system

    Args:
        body: Raw response body
    """
    for fragment in FORBIDDEN_FRAGMENTS:
        assert fragment not in body, f"response leaked {fragment!r}: {body}"


@pytest.mark.parametrize("error", [
    UserCreationError(INTERNAL_TEXT),
    EmailAlreadyExistsError(INTERNAL_TEXT),
])
def test_registration_failures_report_no_internals(error):
    """Whatever the registration failure, the body names the outcome only"""
    app.dependency_overrides[get_registration_service] = lambda: FailingAccountService(error)
    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/accounts/register",
                json={"email": "user@example.com", "password": "StrongPass1!"}
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code >= 400
    assert_no_internals(response.text)


@pytest.mark.parametrize("error", [
    InvalidCredentialsError(INTERNAL_TEXT),
    UserNotFoundError(INTERNAL_TEXT),
])
def test_login_failures_report_no_internals(error):
    """Sign-in refusals never carry the reason they were refused"""
    app.dependency_overrides[get_authentication_service] = lambda: FailingAccountService(error)
    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/accounts/login",
                json={"email": "user@example.com", "password": "StrongPass1!"}
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 401
    assert_no_internals(response.text)


def test_an_unknown_account_and_a_wrong_password_answer_the_same():
    """The refusal does not reveal which accounts exist"""
    answers = []
    for error in (UserNotFoundError(INTERNAL_TEXT), InvalidCredentialsError(INTERNAL_TEXT)):
        app.dependency_overrides[get_authentication_service] = lambda error=error: FailingAccountService(error)
        try:
            with TestClient(app) as client:
                response = client.post(
                    "/api/v1/accounts/login",
                    json={"email": "user@example.com", "password": "StrongPass1!"}
                )
        finally:
            app.dependency_overrides.clear()
        answers.append((response.status_code, response.json()["detail"]))

    assert answers[0] == answers[1]


def test_password_reset_failures_report_no_internals():
    """A reset that could not be started says so without naming the storage"""
    app.dependency_overrides[get_password_service] = lambda: FailingAccountService(
        PasswordResetError(INTERNAL_TEXT)
    )
    try:
        with TestClient(app) as client:
            response = client.post(
                "/api/v1/accounts/password-reset/request",
                json={"email": "user@example.com"}
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code >= 400
    assert_no_internals(response.text)


@pytest.mark.parametrize("error", [
    CartTokenCreationError(INTERNAL_TEXT),
    CartNotFoundError(INTERNAL_TEXT),
    InsufficientStockError(INTERNAL_TEXT),
])
def test_cart_failures_report_no_internals(error):
    """Cart failures describe the outcome, never the statement behind it"""
    app.dependency_overrides[get_cart_service] = lambda: FailingCartService(error)
    try:
        with TestClient(app) as client:
            response = client.post("/api/v1/checkout/cart/token")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code >= 400
    assert_no_internals(response.text)
