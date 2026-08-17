from typing import Any, Dict

import pytest
from fastapi.testclient import TestClient

from apps.accounts.services.social_auth.dependencies import get_social_auth_service_resolver
from main import app
from oauth.exceptions import ConfigurationError, ProviderNotSupportedError

SOCIAL_AUTH_URL = "/api/v1/auth/social-auth"
SUPPORTED = ["google", "facebook"]


class FakeSocialAuthService:
    """Social auth service answering without reaching a provider"""

    def __init__(self, provider: str):
        self.provider = provider

    async def authenticate(self, request) -> Any:
        """Report a successful authentication of a known user"""
        from apps.accounts.services.social_auth.dto import SocialAuthResponse, SocialAuthTokens

        return SocialAuthResponse(
            success=True,
            message="Authenticated",
            provider=self.provider,
            tokens=SocialAuthTokens(access_token="access-token", refresh_token="refresh-token", expires_in=1800),
            user_profile=None,
            is_new_user=False
        )


def resolver_with_broken_facebook(provider_name: str) -> FakeSocialAuthService:
    """
    Resolve Google normally and fail for Facebook the way a missing credential does

    Args:
        provider_name: Provider the caller asked for

    Returns:
        Service for a provider that is configured

    Raises:
        ConfigurationError: If the provider has no usable credentials
        ProviderNotSupportedError: If the provider is unknown
    """
    if provider_name == "google":
        return FakeSocialAuthService("google")
    if provider_name == "facebook":
        raise ConfigurationError("facebook", "client_id is required")
    raise ProviderNotSupportedError(provider_name, SUPPORTED)


@pytest.fixture
def client() -> TestClient:
    """Serve the application with a resolver whose Facebook credentials are missing"""
    app.dependency_overrides[get_social_auth_service_resolver] = lambda: resolver_with_broken_facebook
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_google_login_works_while_facebook_is_misconfigured(client):
    """A credential missing for one provider does not disable the others"""
    response = client.post(SOCIAL_AUTH_URL, json={"provider": "google", "access_token": "a-long-enough-oauth-token"})

    assert response.status_code == 200
    assert response.json()["success"] is True


def test_an_unknown_provider_is_refused_without_touching_the_others(client):
    """An unsupported provider is answered as unsupported, not as a server error"""
    response = client.post(SOCIAL_AUTH_URL, json={"provider": "github", "access_token": "a-long-enough-oauth-token"})

    assert response.status_code == 422


def test_the_misconfigured_provider_reports_itself_as_unavailable(client):
    """Asking for the broken provider names that provider and nothing internal"""
    response = client.post(SOCIAL_AUTH_URL, json={"provider": "facebook", "access_token": "a-long-enough-oauth-token"})

    assert response.status_code == 503
    assert "facebook" in response.json()["detail"]
    assert "client_id" not in response.text


def dependency_functions(path: str) -> set:
    """
    Collect every dependency the endpoint on that path is wired to

    Args:
        path: Route path to inspect

    Returns:
        Names of the dependency callables, including nested ones
    """
    from apps.accounts.routes.social_auth import router

    route = next(candidate for candidate in router.routes if candidate.path.endswith(path.split("/")[-1]))

    names = set()
    pending = list(route.dependant.dependencies)
    while pending:
        dependency = pending.pop()
        if dependency.call is not None:
            names.add(dependency.call.__name__)
        pending.extend(dependency.dependencies)

    return names


def test_the_endpoint_depends_on_the_resolver_not_on_every_provider():
    """Serving one provider must not require the credentials of all of them"""
    wired = dependency_functions(SOCIAL_AUTH_URL)

    assert "get_social_auth_service_resolver" in wired
    assert "get_google_social_auth_service" not in wired
    assert "get_facebook_social_auth_service" not in wired
