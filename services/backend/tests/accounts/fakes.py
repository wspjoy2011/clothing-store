"""Test doubles for the account services."""

from contextlib import asynccontextmanager
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from typing import Any, AsyncIterator, List, Optional

from apps.accounts.dto.users import UserDTO
from db.transaction import get_current_transaction, TransactionState
from notifications.exceptions.email import BaseEmailError
from tests.fakes import FakeConnection, FakeTransactionManager


@dataclass
class SentEmail:
    """Record of one delivery attempt and the transaction state during it"""

    address: str
    kind: str
    inside_transaction: bool


class FakeEmailSender:
    """Email sender recording whether a transaction was open while sending"""

    def __init__(self, fail: bool = False):
        self.fail = fail
        self.sent: List[SentEmail] = []

    async def _record(self, address: str, kind: str) -> None:
        """
        Record a delivery attempt

        Args:
            address: Recipient address
            kind: Which email was requested
        """
        self.sent.append(
            SentEmail(address=address, kind=kind, inside_transaction=get_current_transaction() is not None)
        )
        if self.fail:
            raise BaseEmailError("delivery failed")

    async def send_activation_email(self, email: str, activation_link: str) -> None:
        """Record an activation email"""
        await self._record(email, "activation")

    async def send_resend_activation_email(self, email: str, activation_link: str) -> None:
        """Record a repeated activation email"""
        await self._record(email, "resend_activation")

    async def send_activation_complete_email(self, email: str, login_link: str) -> None:
        """Record an activation complete email"""
        await self._record(email, "activation_complete")

    async def send_password_reset_email(self, email: str, reset_link: str) -> None:
        """Record a password reset email"""
        await self._record(email, "password_reset")

    async def send_password_reset_complete_email(self, email: str, login_link: str) -> None:
        """Record a password reset complete email"""
        await self._record(email, "password_reset_complete")

    async def send_password_change_notification_email(self, email: str, login_link: str, change_time: str) -> None:
        """Record a password change notification"""
        await self._record(email, "password_change")


class FakeUserRepository:
    """User repository backed by an in-memory list"""

    def __init__(self):
        self.users: List[UserDTO] = []
        self.next_id = 1

    async def get_user_by_email(self, email: str) -> Optional[UserDTO]:
        """Find a user by address"""
        return next((user for user in self.users if user.email == email), None)

    async def update_user_status(self, user_id: int, is_active: bool) -> bool:
        """Mark a stored user as active or inactive"""
        for index, user in enumerate(self.users):
            if user.id == user_id:
                self.users[index] = replace(user, is_active=is_active)
                return True
        return False

    async def create_user(self, user_data: Any) -> UserDTO:
        """Store a new user"""
        user = UserDTO(
            id=self.next_id,
            email=user_data.email,
            is_active=False,
            created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            updated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
            group_id=user_data.group_id,
            group_name="user"
        )
        self.next_id += 1
        self.users.append(user)
        return user


class FakeUserGroupRepository:
    """User group repository returning one default group"""

    def __init__(self, group_id: int = 1, name: str = "user"):
        self.group = type("Group", (), {"id": group_id, "name": name})()

    async def get_group_by_name(self, name: str) -> Any:
        """Return the default group regardless of the requested name"""
        return self.group


class FakeTokenRepository:
    """Token repository that can be told to fail"""

    def __init__(self, fail_on_create: Optional[Exception] = None):
        self.fail_on_create = fail_on_create
        self.created: List[Any] = []

    async def create_activation_token(self, token_data: Any) -> Any:
        """Store an activation token or raise the configured failure"""
        if self.fail_on_create is not None:
            raise self.fail_on_create

        self.created.append(token_data)
        return token_data


class FakePasswordManager:
    """Password manager performing a reversible transformation"""

    @staticmethod
    async def hash_password(password: str) -> str:
        """Return a recognisable stand-in for a hash"""
        return f"hashed:{password}"

    @staticmethod
    async def verify_password(plain: str, hashed: str) -> bool:
        """Compare against the stand-in hash"""
        return hashed == f"hashed:{plain}"


class FakeJWTManager:
    """JWT manager returning fixed tokens"""

    @staticmethod
    def create_access_token(payload: dict) -> str:
        """Return a fixed access token"""
        return "access-token"

    @staticmethod
    def create_refresh_token(payload: dict) -> str:
        """Return a fixed refresh token"""
        return "refresh-token"

    @staticmethod
    def get_token_expiration(token: str) -> datetime:
        """Return a fixed expiration far enough in the future"""
        return datetime(2027, 1, 1, tzinfo=timezone.utc)
