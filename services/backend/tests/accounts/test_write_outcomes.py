from typing import Any, List, Optional

import pytest

from apps.accounts.dto.password_reset import PasswordChangeDTO
from apps.accounts.repositories.token import TokenRepository
from apps.accounts.repositories.user import UserRepository
from apps.accounts.services.exceptions import PasswordChangeError
from apps.accounts.services.password import PasswordService
from db.query_builder import SQLQueryBuilder
from tests.accounts.fakes import (
    FakeEmailSender,
    FakePasswordManager,
    FakeTokenRepository,
    FakeTransactionManager,
    FakeUserRepository,
)

STORED_HASH = "hashed:current"


class CountingDAO:
    """DAO reporting a configured number of affected rows"""

    def __init__(self, affected: int):
        self.affected = affected
        self.writes: List[str] = []

    async def execute(self, query: str, params: Optional[List[Any]] = None, **kwargs: Any) -> None:
        """Answer reads with nothing"""
        return None

    async def execute_write(self, query: str, params: Optional[List[Any]] = None) -> int:
        """Record the statement and report the configured count"""
        self.writes.append(query)
        return self.affected


def build_user_repository(affected: int) -> tuple:
    """
    Assemble a user repository over a DAO with a known outcome

    Args:
        affected: Rows the statements should report as changed

    Returns:
        Repository and the DAO behind it
    """
    dao = CountingDAO(affected)
    return UserRepository(dao, SQLQueryBuilder("accounts_users")), dao


async def test_updating_the_password_of_a_missing_user_reports_failure():
    """A statement that matched no row is not success"""
    repository, _ = build_user_repository(affected=0)

    assert await repository.update_user_password(999, "new-hash") is False


async def test_updating_the_password_of_a_stored_user_reports_success():
    """A statement that changed a row reports success"""
    repository, _ = build_user_repository(affected=1)

    assert await repository.update_user_password(1, "new-hash") is True


async def test_deactivating_a_missing_user_reports_failure():
    """Status updates answer from the row count too"""
    repository, _ = build_user_repository(affected=0)

    assert await repository.update_user_status(999, False) is False


async def test_deleting_a_missing_user_reports_failure():
    """Deletions answer from the row count as well"""
    repository, _ = build_user_repository(affected=0)

    assert await repository.delete_user(999) is False


async def test_deleting_tokens_reports_how_many_were_removed():
    """The count of removed refresh tokens is the count the database reported"""
    dao = CountingDAO(affected=4)
    repository = TokenRepository(dao, SQLQueryBuilder("accounts_refresh_tokens"))

    assert await repository.delete_user_refresh_tokens(1) == 4


async def test_deleting_a_token_that_is_not_there_reports_failure():
    """Removing an absent activation token is reported as nothing removed"""
    dao = CountingDAO(affected=0)
    repository = TokenRepository(dao, SQLQueryBuilder("accounts_activation_tokens"))

    assert await repository.delete_activation_token("unknown-token") is False


class RepositoryWithoutTheUser(FakeUserRepository):
    """User repository that finds the user, then loses it before the write"""

    async def get_hashed_password_by_email(self, email: str) -> Optional[str]:
        """Report the stored hash"""
        return STORED_HASH

    async def update_user_password(self, user_id: int, hashed_password: str) -> bool:
        """Report that the row is gone by the time the write ran"""
        self.password_updates.append((user_id, hashed_password))
        return False


async def test_a_password_change_that_wrote_nothing_is_not_reported_as_done():
    """The user is told the change failed instead of getting a false confirmation"""
    repository = RepositoryWithoutTheUser()
    await repository.create_user(type("Data", (), {"email": "user@example.com", "group_id": 1})())
    email_sender = FakeEmailSender()
    transactions = FakeTransactionManager()

    service = PasswordService(
        user_repository=repository,
        token_repository=FakeTokenRepository(),
        password_manager=FakePasswordManager(),
        email_sender=email_sender,
        transaction_manager=transactions
    )

    with pytest.raises(PasswordChangeError):
        await service.change_password(
            "user@example.com",
            PasswordChangeDTO(old_password="current", new_password="Different123!")
        )

    assert email_sender.sent == []
    assert transactions.rolled_back == 1
