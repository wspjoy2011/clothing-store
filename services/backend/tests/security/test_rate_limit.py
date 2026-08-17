from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from apps.accounts.dependencies import get_authentication_service, get_registration_service
from apps.accounts.dto.users import UserDTO
from main import app
from security.rate_limit import limiter

REGISTRATION_URL = "/api/v1/accounts/register"
LOGIN_URL = "/api/v1/accounts/login"
REGISTRATION_LIMIT_PER_MINUTE = 5


class FakeRegistrationService:
    """Registration service that registers anybody without touching a database"""

    def __init__(self):
        self.registrations = 0

    async def register_user(self, create_user_dto) -> UserDTO:
        """Count the registration and answer with a stored user"""
        self.registrations += 1
        now = datetime(2026, 1, 1, tzinfo=timezone.utc)
        return UserDTO(
            id=self.registrations,
            email=create_user_dto.email,
            is_active=False,
            created_at=now,
            updated_at=now,
            group_id=1,
            group_name="user"
        )


class FakeAuthenticationService:
    """Authentication service that never has to be reached"""

    async def login_user(self, login_dto):
        """Refuse any sign-in, since no test here should get this far"""
        raise AssertionError("the schema should have refused this request before the service")


@pytest.fixture
def service() -> FakeRegistrationService:
    """Serve fake account services to the application and reset the limiter

    Both are overridden: leaving one real would make the application build a
    connection pool while resolving dependencies, and the test would wait out its
    timeout instead of exercising the endpoint.
    """
    limiter.reset()
    fake = FakeRegistrationService()
    app.dependency_overrides[get_registration_service] = lambda: fake
    app.dependency_overrides[get_authentication_service] = lambda: FakeAuthenticationService()
    yield fake
    app.dependency_overrides.clear()
    limiter.reset()


def register(client: TestClient, index: int):
    """
    Send one registration request

    Args:
        client: Client bound to the application
        index: Number making the email unique

    Returns:
        The HTTP response
    """
    return client.post(
        REGISTRATION_URL,
        json={"email": f"user{index}@example.com", "password": "StrongPass1!"}
    )


def test_registrations_beyond_the_limit_are_refused(service):
    """A burst of registrations from one address is cut off instead of served"""
    with TestClient(app) as client:
        statuses = [register(client, index).status_code for index in range(REGISTRATION_LIMIT_PER_MINUTE + 2)]

    assert statuses.count(429) == 2
    assert service.registrations == REGISTRATION_LIMIT_PER_MINUTE


def test_the_refusal_says_what_to_do_and_nothing_about_the_limit(service):
    """The 429 body asks the caller to retry and never states the configured rate"""
    with TestClient(app) as client:
        for index in range(REGISTRATION_LIMIT_PER_MINUTE):
            register(client, index)
        response = register(client, 99)

    assert response.status_code == 429
    detail = response.json()["detail"]
    assert "minute" in detail
    assert "per" not in detail
    assert str(REGISTRATION_LIMIT_PER_MINUTE) not in detail


def test_work_stops_at_the_limit_rather_than_after_it(service):
    """A refused request never reaches the service, so argon2 is never run for it"""
    with TestClient(app) as client:
        for index in range(REGISTRATION_LIMIT_PER_MINUTE + 3):
            register(client, index)

    assert service.registrations == REGISTRATION_LIMIT_PER_MINUTE


def test_a_password_beyond_the_maximum_is_rejected_before_hashing(service):
    """An oversized password is refused by the schema, not carried into argon2"""
    with TestClient(app) as client:
        response = client.post(LOGIN_URL, json={"email": "user@example.com", "password": "x" * 5000})

    assert response.status_code == 422
