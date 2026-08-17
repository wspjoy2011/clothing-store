from datetime import datetime, timedelta, timezone
from typing import Any, List, Optional

import pytest

from apps.accounts.dto.activation import ActivateAccountDTO
from apps.accounts.dto.password_reset import PasswordResetConfirmDTO
from apps.accounts.dto.tokens import ActivationTokenDTO, PasswordResetTokenDTO
from apps.accounts.dto.users import UserDTO
from apps.accounts.services.exceptions import (
    ExpiredActivationTokenError,
    ExpiredPasswordResetTokenError,
    PasswordResetTokenNotFoundError,
)
from apps.accounts.services.password import PasswordService
from apps.accounts.services.registration import RegistrationService
from tests.accounts.fakes import (
    FakeEmailSender,
    FakePasswordManager,
    FakeTransactionManager,
    FakeUserGroupRepository,
    FakeUserRepository,
)

ADDRESS = "user@example.com"
TOKEN = "a-token-that-exists"
NOW = datetime.now(timezone.utc)


class ExpiringTokenRepository:
    """Token repository serving one token with a chosen expiry"""

    def __init__(self, expires_at: Optional[datetime], exists: bool = True):
        self.expires_at = expires_at
        self.exists = exists
        self.deleted: List[str] = []

    async def get_activation_token_by_token(self, token: str) -> Optional[ActivationTokenDTO]:
        """Serve the stored activation token regardless of its expiry"""
        if not self.exists:
            return None
        return ActivationTokenDTO(id=1, token=token, expires_at=self.expires_at, user_id=1)

    async def get_activation_token_by_email_and_token(self, email: str, token: str) -> Optional[ActivationTokenDTO]:
        """Serve the stored activation token for that address regardless of expiry"""
        return await self.get_activation_token_by_token(token)

    async def get_password_reset_token_by_token(self, token: str) -> Optional[PasswordResetTokenDTO]:
        """Serve the stored reset token regardless of its expiry"""
        if not self.exists:
            return None
        return PasswordResetTokenDTO(id=1, token=token, expires_at=self.expires_at, user_id=1)

    async def delete_activation_token(self, token: str) -> bool:
        """Record the removal"""
        self.deleted.append(token)
        return True

    async def delete_password_reset_token(self, token: str) -> bool:
        """Record the removal"""
        self.deleted.append(token)
        return True

    async def delete_user_refresh_tokens(self, user_id: int) -> int:
        """Report no sessions to revoke"""
        return 0


class RepositoryWithUser(FakeUserRepository):
    """User repository holding one inactive user"""

    def __init__(self):
        super().__init__()
        self.users.append(
            UserDTO(
                id=1,
                email=ADDRESS,
                is_active=False,
                created_at=NOW,
                updated_at=NOW,
                group_id=1,
                group_name="user"
            )
        )

    async def get_user_by_id(self, user_id: int) -> Optional[UserDTO]:
        """Find the stored user by identifier"""
        return next((user for user in self.users if user.id == user_id), None)


def build_registration_service(tokens: ExpiringTokenRepository) -> RegistrationService:
    """
    Assemble a registration service around one stored token

    Args:
        tokens: Repository serving the token under test

    Returns:
        Service wired for the test
    """
    return RegistrationService(
        user_repository=RepositoryWithUser(),
        user_group_repository=FakeUserGroupRepository(),
        token_repository=tokens,
        password_manager=FakePasswordManager(),
        email_sender=FakeEmailSender(),
        transaction_manager=FakeTransactionManager()
    )


def build_password_service(tokens: ExpiringTokenRepository) -> PasswordService:
    """
    Assemble the password service around one stored token

    Args:
        tokens: Repository serving the token under test

    Returns:
        Service wired for the test
    """
    return PasswordService(
        user_repository=RepositoryWithUser(),
        token_repository=tokens,
        password_manager=FakePasswordManager(),
        email_sender=FakeEmailSender(),
        transaction_manager=FakeTransactionManager()
    )


async def test_an_expired_reset_token_is_reported_as_expired():
    """An expired link is answered as expired, not as an unknown token"""
    tokens = ExpiringTokenRepository(expires_at=NOW - timedelta(hours=1))
    service = build_password_service(tokens)

    with pytest.raises(ExpiredPasswordResetTokenError):
        await service.confirm_password_reset(
            PasswordResetConfirmDTO(token=TOKEN, new_password="Password123!")
        )


async def test_an_unknown_reset_token_is_reported_as_not_found():
    """A token nobody issued is still answered as not found"""
    tokens = ExpiringTokenRepository(expires_at=None, exists=False)
    service = build_password_service(tokens)

    with pytest.raises(PasswordResetTokenNotFoundError):
        await service.confirm_password_reset(
            PasswordResetConfirmDTO(token=TOKEN, new_password="Password123!")
        )


async def test_an_expired_reset_token_is_removed_when_it_is_refused():
    """The dead token is cleaned up rather than left to be tried again"""
    tokens = ExpiringTokenRepository(expires_at=NOW - timedelta(hours=1))
    service = build_password_service(tokens)

    with pytest.raises(ExpiredPasswordResetTokenError):
        await service.confirm_password_reset(
            PasswordResetConfirmDTO(token=TOKEN, new_password="Password123!")
        )

    assert tokens.deleted == [TOKEN]


async def test_an_expired_activation_token_is_reported_as_expired():
    """Activation answers the same way: expired is not the same as unknown"""
    tokens = ExpiringTokenRepository(expires_at=NOW - timedelta(days=2))
    service = build_registration_service(tokens)

    with pytest.raises(ExpiredActivationTokenError):
        await service.activate_account(ActivateAccountDTO(email=ADDRESS, token=TOKEN))


class QueryRecordingDAO:
    """DAO recording the statements it was asked to run"""

    def __init__(self):
        self.queries: List[str] = []

    async def execute(self, query: str, params: Optional[List[Any]] = None, **kwargs: Any) -> None:
        """Record the statement and report no row"""
        self.queries.append(query)
        return None


async def test_looking_up_a_reset_token_does_not_filter_on_expiry():
    """The lookup answers for an expired token too, leaving the decision to the service"""
    from apps.accounts.repositories.token import TokenRepository
    from db.query_builder import SQLQueryBuilder

    dao = QueryRecordingDAO()
    repository = TokenRepository(dao, SQLQueryBuilder("accounts_password_reset_tokens"))

    await repository.get_password_reset_token_by_token(TOKEN)

    condition = dao.queries[0].split("WHERE", 1)[1]
    assert "expires_at" not in condition


async def test_looking_up_an_activation_token_does_not_filter_on_expiry():
    """Activation lookups answer the same way, so expiry stays one decision in one place"""
    from apps.accounts.repositories.token import TokenRepository
    from db.query_builder import SQLQueryBuilder

    dao = QueryRecordingDAO()
    repository = TokenRepository(dao, SQLQueryBuilder("accounts_activation_tokens"))

    await repository.get_activation_token_by_token(TOKEN)

    condition = dao.queries[0].split("WHERE", 1)[1]
    assert "expires_at" not in condition
