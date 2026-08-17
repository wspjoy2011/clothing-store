from datetime import datetime, timezone
from typing import Any, List, Optional

import pytest

from apps.accounts.dto.password_reset import PasswordChangeDTO
from apps.accounts.dto.users import UserDTO
from apps.accounts.services.account import AccountService
from tests.accounts.fakes import (
    FakeEmailSender,
    FakeJWTManager,
    FakePasswordManager,
    FakeTransactionManager,
    FakeUserGroupRepository,
    FakeUserRepository,
)

ADDRESS = "user@example.com"
STORED_HASH = "hashed:current"
PRESENTED_REFRESH = "old-refresh-token"


class SessionTokenRepository:
    """Token repository tracking issued and revoked refresh tokens"""

    def __init__(self, stored_refresh: Optional[str] = PRESENTED_REFRESH):
        self.stored_refresh = stored_refresh
        self.created: List[Any] = []
        self.deleted: List[str] = []
        self.revoked_users: List[int] = []
        self.revoked_inside_transaction: List[bool] = []

    async def get_refresh_token_by_token(self, token: str) -> Optional[object]:
        """Report the stored refresh token when it matches"""
        if self.stored_refresh is not None and token == self.stored_refresh:
            return type("StoredToken", (), {"token": token, "user_id": 1})()
        return None

    async def create_refresh_token(self, token_data: Any) -> Any:
        """Store a newly issued refresh token"""
        self.created.append(token_data)
        return token_data

    async def delete_refresh_token(self, token: str) -> bool:
        """Forget one refresh token"""
        self.deleted.append(token)
        if token == self.stored_refresh:
            self.stored_refresh = None
            return True
        return False

    async def delete_user_refresh_tokens(self, user_id: int) -> int:
        """Forget every refresh token of a user and record the context"""
        from db.transaction import get_current_transaction

        self.revoked_users.append(user_id)
        self.revoked_inside_transaction.append(get_current_transaction() is not None)
        self.stored_refresh = None
        return 2


class RepositoryWithActiveUser(FakeUserRepository):
    """User repository holding one active user with a known password"""

    def __init__(self):
        super().__init__()
        self.users.append(
            UserDTO(
                id=1,
                email=ADDRESS,
                is_active=True,
                created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
                updated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
                group_id=1,
                group_name="user"
            )
        )

    async def get_hashed_password_by_email(self, email: str) -> Optional[str]:
        """Report the stored hash"""
        return STORED_HASH

    async def get_user_by_id(self, user_id: int) -> Optional[UserDTO]:
        """Find the stored user by identifier"""
        return next((user for user in self.users if user.id == user_id), None)


def build_service(tokens: SessionTokenRepository, transactions: FakeTransactionManager) -> AccountService:
    """
    Assemble an account service around one active user

    Args:
        tokens: Repository tracking refresh tokens
        transactions: Manager exposing transaction state

    Returns:
        Service wired for the test
    """
    return AccountService(
        user_repository=RepositoryWithActiveUser(),
        user_group_repository=FakeUserGroupRepository(),
        token_repository=tokens,
        password_manager=FakePasswordManager(),
        jwt_manager=FakeJWTManager(),
        email_sender=FakeEmailSender(),
        transaction_manager=transactions
    )


async def test_changing_the_password_revokes_the_issued_sessions():
    """A stolen refresh token stops working once the owner changes the password"""
    tokens = SessionTokenRepository()
    transactions = FakeTransactionManager()
    service = build_service(tokens, transactions)

    await service.change_password(
        ADDRESS,
        PasswordChangeDTO(old_password="current", new_password="Different123!")
    )

    assert tokens.revoked_users == [1]
    assert transactions.committed == 1


async def test_the_sessions_are_revoked_in_the_transaction_that_writes_the_password():
    """Revocation and the new password commit together or not at all"""
    tokens = SessionTokenRepository()
    service = build_service(tokens, FakeTransactionManager())

    await service.change_password(
        ADDRESS,
        PasswordChangeDTO(old_password="current", new_password="Different123!")
    )

    assert tokens.revoked_inside_transaction == [True]


async def test_refreshing_replaces_the_token_that_was_presented():
    """The presented refresh token is invalidated as part of the exchange"""
    tokens = SessionTokenRepository()
    service = build_service(tokens, FakeTransactionManager())

    result = await service.refresh_access_token(PRESENTED_REFRESH)

    assert tokens.deleted == [PRESENTED_REFRESH]
    assert len(tokens.created) == 1
    assert result.refresh_token == "refresh-token"
    assert result.access_token == "access-token"


async def test_a_rotated_token_cannot_be_used_again():
    """Presenting the exchanged token a second time is refused"""
    from apps.accounts.services.exceptions import InvalidRefreshTokenError

    tokens = SessionTokenRepository()
    service = build_service(tokens, FakeTransactionManager())

    await service.refresh_access_token(PRESENTED_REFRESH)

    with pytest.raises(InvalidRefreshTokenError):
        await service.refresh_access_token(PRESENTED_REFRESH)


async def test_the_rotation_is_one_unit_of_work():
    """Removing the old token and storing the new one commit together"""
    tokens = SessionTokenRepository()
    transactions = FakeTransactionManager()
    service = build_service(tokens, transactions)

    await service.refresh_access_token(PRESENTED_REFRESH)

    assert transactions.committed == 1
    assert transactions.rolled_back == 0
