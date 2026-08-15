import pytest

import apps.accounts.services.social_auth.service as service_module
from apps.accounts.services.social_auth.dto import SocialAuthRequest
from apps.accounts.services.social_auth.service import SocialAuthService
from oauth.dto import OAuthUserInfo
from tests.accounts.fakes import (
    FakeEmailSender,
    FakeJWTManager,
    FakePasswordManager,
    FakeTokenRepository,
    FakeTransactionManager,
    FakeUserGroupRepository,
    FakeUserRepository,
)


@pytest.fixture(autouse=True)
def email_validation_without_dns(monkeypatch):
    """Keep profile validation offline: the real validator resolves MX records"""

    def accept_address(email: str, **options):
        return type("ValidatedEmail", (), {"normalized": email})()

    monkeypatch.setattr(service_module, "validate_email", accept_address)


class FakeOAuthProvider:
    """OAuth provider returning a fixed verified profile"""

    provider_name = "google"

    def __init__(self, email: str = "social@example.com"):
        self.email = email

    async def authenticate_user(self, access_token: str) -> OAuthUserInfo:
        """Return the profile the provider would have fetched"""
        return OAuthUserInfo(
            provider="google",
            provider_id="provider-id-1",
            email=self.email,
            name="Social User",
            verified_email=True
        )


class RecordingTokenRepository(FakeTokenRepository):
    """Token repository accepting the refresh tokens issued after authentication"""

    def __init__(self):
        super().__init__()
        self.refresh_tokens = []

    async def create_refresh_token(self, token_data) -> object:
        """Store a refresh token"""
        self.refresh_tokens.append(token_data)
        return token_data

    async def delete_user_refresh_tokens(self, user_id: int) -> bool:
        """Drop previously issued refresh tokens"""
        self.refresh_tokens.clear()
        return True


def build_service(email_sender: FakeEmailSender, transaction_manager: FakeTransactionManager) -> SocialAuthService:
    """
    Assemble a social auth service from test doubles

    Args:
        email_sender: Sender recording deliveries
        transaction_manager: Manager exposing transaction state

    Returns:
        Service wired for the test
    """
    return SocialAuthService(
        oauth_provider=FakeOAuthProvider(),
        user_repository=FakeUserRepository(),
        user_group_repository=FakeUserGroupRepository(),
        token_repository=RecordingTokenRepository(),
        password_manager=FakePasswordManager(),
        jwt_manager=FakeJWTManager(),
        email_sender=email_sender,
        transaction_manager=transaction_manager
    )


async def test_welcome_email_is_sent_outside_the_transaction():
    """A social registration delivers its welcome email after the transaction closed"""
    email_sender = FakeEmailSender()
    transaction_manager = FakeTransactionManager()
    service = build_service(email_sender, transaction_manager)

    response = await service.authenticate(SocialAuthRequest(provider="google", access_token="token"))

    assert response.success is True
    assert [email.kind for email in email_sender.sent] == ["activation_complete"]
    assert email_sender.sent[0].inside_transaction is False
    assert transaction_manager.committed == 1


async def test_welcome_email_failure_does_not_fail_authentication():
    """Delivery failure leaves the user authenticated"""
    email_sender = FakeEmailSender(fail=True)
    transaction_manager = FakeTransactionManager()
    service = build_service(email_sender, transaction_manager)

    response = await service.authenticate(SocialAuthRequest(provider="google", access_token="token"))

    assert response.success is True
    assert transaction_manager.committed == 1
