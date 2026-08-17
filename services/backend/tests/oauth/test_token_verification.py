from typing import Any, Dict, List

import httpx
import pytest

from oauth.exceptions import TokenVerificationError
from oauth.providers.facebook import FacebookOAuthProvider
from oauth.providers.google import GoogleOAuthProvider

OUR_CLIENT_ID = "ours.apps.googleusercontent.com"
OUR_SECRET = "our-secret"
ATTACKER_CLIENT_ID = "attacker.apps.googleusercontent.com"
OUR_APP_ID = "1234567890"
ATTACKER_APP_ID = "9876543210"


class FakeResponse:
    """HTTP response carrying a preloaded payload"""

    def __init__(self, status_code: int, payload: Dict[str, Any]):
        self.status_code = status_code
        self._payload = payload
        self.text = str(payload)

    def json(self) -> Dict[str, Any]:
        """Return the preloaded payload"""
        return self._payload


class FakeHTTPClient:
    """HTTP client answering from a queue and recording the URLs it was asked for"""

    requested: List[str] = []
    responses: List[FakeResponse] = []

    def __init__(self, *args: Any, **kwargs: Any):
        pass

    async def __aenter__(self) -> "FakeHTTPClient":
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> bool:
        return False

    async def get(self, url: str, **kwargs: Any) -> FakeResponse:
        """Record the URL and answer with the next queued response"""
        type(self).requested.append(url)
        return type(self).responses.pop(0)


@pytest.fixture(autouse=True)
def fake_http(monkeypatch) -> type:
    """Replace the HTTP client with one answering from a queue"""
    FakeHTTPClient.requested = []
    FakeHTTPClient.responses = []
    monkeypatch.setattr(httpx, "AsyncClient", FakeHTTPClient)
    return FakeHTTPClient


def build_google() -> GoogleOAuthProvider:
    """Build a Google provider configured with our own credentials"""
    return GoogleOAuthProvider(client_id=OUR_CLIENT_ID, client_secret=OUR_SECRET)


def build_facebook() -> FacebookOAuthProvider:
    """Build a Facebook provider configured with our own credentials"""
    return FacebookOAuthProvider(client_id=OUR_APP_ID, client_secret=OUR_SECRET)


async def test_google_refuses_a_token_issued_to_another_application(fake_http):
    """A valid Google token belonging to somebody else's client cannot sign anybody in"""
    fake_http.responses = [
        FakeResponse(200, {"aud": ATTACKER_CLIENT_ID, "email": "victim@example.com"})
    ]
    provider = build_google()

    with pytest.raises(TokenVerificationError):
        await provider.verify_token("token-of-the-victim")

    assert not any("userinfo" in url for url in fake_http.requested)


async def test_google_accepts_a_token_issued_to_us(fake_http):
    """A token whose audience is our own client is accepted and its profile read"""
    fake_http.responses = [
        FakeResponse(200, {"aud": OUR_CLIENT_ID}),
        FakeResponse(200, {"id": "1", "email": "user@example.com", "name": "User"})
    ]
    provider = build_google()

    profile = await provider.verify_token("our-token")

    assert profile["email"] == "user@example.com"
    assert any("userinfo" in url for url in fake_http.requested)


async def test_google_refuses_a_token_it_cannot_look_up(fake_http):
    """A token Google does not recognise is refused before the profile is read"""
    fake_http.responses = [FakeResponse(400, {"error": "invalid_token"})]
    provider = build_google()

    with pytest.raises(TokenVerificationError):
        await provider.verify_token("made-up-token")

    assert not any("userinfo" in url for url in fake_http.requested)


async def test_google_treats_an_unstated_email_confirmation_as_unconfirmed():
    """An absent verified_email means unconfirmed, so the account cannot be claimed"""
    provider = build_google()

    info = provider.extract_user_info({"id": "1", "email": "user@example.com", "name": "User"})

    assert info.verified_email is False


async def test_facebook_refuses_a_token_of_another_app(fake_http):
    """A valid Facebook token belonging to another app cannot sign anybody in"""
    fake_http.responses = [
        FakeResponse(200, {"data": {"is_valid": True, "app_id": ATTACKER_APP_ID}})
    ]
    provider = build_facebook()

    with pytest.raises(TokenVerificationError):
        await provider.verify_token("token-of-the-victim")

    assert not any(url.endswith("/me") for url in fake_http.requested)


async def test_facebook_refuses_a_token_reported_invalid(fake_http):
    """A token Facebook reports as invalid is refused even when the app matches"""
    fake_http.responses = [
        FakeResponse(200, {"data": {"is_valid": False, "app_id": OUR_APP_ID}})
    ]
    provider = build_facebook()

    with pytest.raises(TokenVerificationError):
        await provider.verify_token("expired-token")

    assert not any(url.endswith("/me") for url in fake_http.requested)


async def test_facebook_accepts_a_token_of_our_app(fake_http):
    """A valid token issued to our own app is accepted and its profile read"""
    fake_http.responses = [
        FakeResponse(200, {"data": {"is_valid": True, "app_id": OUR_APP_ID}}),
        FakeResponse(200, {"id": "1", "email": "user@example.com", "name": "User"})
    ]
    provider = build_facebook()

    profile = await provider.verify_token("our-token")

    assert profile["email"] == "user@example.com"
    assert any(url.endswith("/me") for url in fake_http.requested)
