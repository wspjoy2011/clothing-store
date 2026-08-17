"""Test doubles for the account services."""

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from typing import Any, List, Optional

from apps.accounts.dto.users import UserDTO
from db.transaction import get_current_transaction
from notifications.exceptions.email import BaseEmailError
from tests.fakes import FakeTransactionManager

# Re-exported for the account tests
__all__ = [
    "FakeEmailSender",
    "FakeJWTManager",
    "FakePasswordManager",
    "FakeTokenRepository",
    "FakeTransactionManager",
    "FakeUserGroupRepository",
    "FakeUserRepository",
    "SentEmail",
]


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
    """User repository backed by an in-memory list

    Writes answer the way the real ones do, from the number of rows they matched:
    updating somebody who is not there reports False rather than success.
    """

    def __init__(self):
        self.users: List[UserDTO] = []
        self.next_id = 1
        self.password_updates: List[tuple] = []

    async def get_user_by_email(self, email: str) -> Optional[UserDTO]:
        """Find a user by address"""
        return next((user for user in self.users if user.email == email), None)

    async def get_user_password_hash(self, user_id: int) -> Optional[str]:
        """Report the stored hash of a user"""
        return next(("hashed:stored" for user in self.users if user.id == user_id), None)

    async def update_user_password(self, user_id: int, hashed_password: str) -> bool:
        """Record the update and report whether any stored user matched"""
        self.password_updates.append((user_id, hashed_password))
        return any(user.id == user_id for user in self.users)

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
    """Password manager performing a reversible transformation

    Every hashing call records whether a transaction was open at the time. The
    real one costs tens of milliseconds of CPU, so hashing while holding a pooled
    connection is what exhausts the pool under a burst of registrations.
    """

    def __init__(self):
        self.hashed_inside_transaction: List[bool] = []

    async def hash_password(self, password: str) -> str:
        """Record the transaction state and return a recognisable stand-in"""
        from db.transaction import get_current_transaction

        self.hashed_inside_transaction.append(get_current_transaction() is not None)
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

    @staticmethod
    def verify_refresh_token(token: str) -> dict:
        """Report the payload a valid refresh token would carry"""
        return {"user_id": 1, "email": "user@example.com", "group_id": 1, "group_name": "user", "type": "refresh"}
