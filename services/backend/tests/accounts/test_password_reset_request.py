from datetime import datetime, timezone
from typing import Any, List, Optional

import pytest

from apps.accounts.dto.password_reset import PasswordResetRequestDTO
from apps.accounts.dto.users import UserDTO
from apps.accounts.repositories.exceptions import TokenCreationError
from apps.accounts.services.account import AccountService
from apps.accounts.services.exceptions import PasswordResetError
from tests.accounts.fakes import (
    FakeEmailSender,
    FakeJWTManager,
    FakePasswordManager,
    FakeTransactionManager,
    FakeUserGroupRepository,
    FakeUserRepository,
)

ADDRESS = "user@example.com"


class ResetTokenRepository:
    """Token repository recording the replacement of reset tokens"""

    def __init__(self, fail_on_create: bool = False):
        self.fail_on_create = fail_on_create
        self.deletions: List[int] = []
        self.created: List[Any] = []
        self.deleted_inside_transaction: List[bool] = []

    async def delete_password_reset_tokens_by_user_id(self, user_id: int) -> bool:
        """Record the deletion and whether a transaction was open"""
        from db.transaction import get_current_transaction

        self.deletions.append(user_id)
        self.deleted_inside_transaction.append(get_current_transaction() is not None)
        return True

    async def create_password_reset_token(self, token_data: Any) -> Any:
        """Store the replacement token or fail as configured"""
        if self.fail_on_create:
            raise TokenCreationError("token storage unavailable")

        self.created.append(token_data)
        return token_data


class RepositoryWithActiveUser(FakeUserRepository):
    """User repository holding one active user"""

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


def build_service(
        token_repository: ResetTokenRepository,
        email_sender: FakeEmailSender,
        transactions: FakeTransactionManager
) -> AccountService:
    """
    Assemble an account service around one active user

    Args:
        token_repository: Repository issuing reset tokens
        email_sender: Sender recording deliveries
        transactions: Manager exposing transaction state

    Returns:
        Service wired for the test
    """
    return AccountService(
        user_repository=RepositoryWithActiveUser(),
        user_group_repository=FakeUserGroupRepository(),
        token_repository=token_repository,
        password_manager=FakePasswordManager(),
        jwt_manager=FakeJWTManager(),
        email_sender=email_sender,
        transaction_manager=transactions
    )


async def test_the_previous_token_is_replaced_inside_one_transaction():
    """Removing the old token and issuing the new one is a single unit of work"""
    tokens = ResetTokenRepository()
    transactions = FakeTransactionManager()
    service = build_service(tokens, FakeEmailSender(), transactions)

    await service.request_password_reset(PasswordResetRequestDTO(email=ADDRESS))

    assert tokens.deleted_inside_transaction == [True]
    assert transactions.committed == 1


async def test_a_lost_replacement_token_is_not_reported_as_a_sent_email():
    """When the new token cannot be stored the caller is told to try again"""
    tokens = ResetTokenRepository(fail_on_create=True)
    email_sender = FakeEmailSender()
    transactions = FakeTransactionManager()
    service = build_service(tokens, email_sender, transactions)

    with pytest.raises(PasswordResetError):
        await service.request_password_reset(PasswordResetRequestDTO(email=ADDRESS))

    assert email_sender.sent == []
    assert transactions.rolled_back == 1


async def test_the_failure_reported_to_the_caller_carries_no_internals():
    """The message names the outcome, not the storage that failed"""
    tokens = ResetTokenRepository(fail_on_create=True)
    service = build_service(tokens, FakeEmailSender(), FakeTransactionManager())

    with pytest.raises(PasswordResetError) as failure:
        await service.request_password_reset(PasswordResetRequestDTO(email=ADDRESS))

    message = str(failure.value).lower()
    assert "token" not in message
    assert "storage" not in message


async def test_the_reset_email_is_sent_outside_the_transaction():
    """Delivery happens after the token was committed, not while holding it open"""
    email_sender = FakeEmailSender()
    service = build_service(ResetTokenRepository(), email_sender, FakeTransactionManager())

    await service.request_password_reset(PasswordResetRequestDTO(email=ADDRESS))

    assert [email.kind for email in email_sender.sent] == ["password_reset"]
    assert email_sender.sent[0].inside_transaction is False


async def test_an_unknown_address_is_answered_as_success():
    """An address nobody registered gets the same answer, revealing nothing"""
    tokens = ResetTokenRepository()
    service = AccountService(
        user_repository=FakeUserRepository(),
        user_group_repository=FakeUserGroupRepository(),
        token_repository=tokens,
        password_manager=FakePasswordManager(),
        jwt_manager=FakeJWTManager(),
        email_sender=FakeEmailSender(),
        transaction_manager=FakeTransactionManager()
    )

    assert await service.request_password_reset(PasswordResetRequestDTO(email="nobody@example.com")) is True
    assert tokens.deletions == []
