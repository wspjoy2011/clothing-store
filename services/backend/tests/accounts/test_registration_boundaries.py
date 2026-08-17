import pytest

from apps.accounts.dto.users import CreateUserDTO
from apps.accounts.repositories.exceptions import TokenCreationError
from apps.accounts.services.account import AccountService
from apps.accounts.services.exceptions import UserCreationError
from tests.accounts.fakes import (
    FakeEmailSender,
    FakeJWTManager,
    FakePasswordManager,
    FakeTokenRepository,
    FakeTransactionManager,
    FakeUserGroupRepository,
    FakeUserRepository,
)


def build_service(
        token_repository: FakeTokenRepository,
        email_sender: FakeEmailSender,
        transaction_manager: FakeTransactionManager
) -> AccountService:
    """
    Assemble an account service from test doubles

    Args:
        token_repository: Repository issuing activation tokens
        email_sender: Sender recording deliveries
        transaction_manager: Manager exposing transaction state

    Returns:
        Service wired for the test
    """
    return AccountService(
        user_repository=FakeUserRepository(),
        user_group_repository=FakeUserGroupRepository(),
        token_repository=token_repository,
        password_manager=FakePasswordManager(),
        jwt_manager=FakeJWTManager(),
        email_sender=email_sender,
        transaction_manager=transaction_manager
    )


async def test_activation_email_is_sent_outside_the_transaction():
    """Registration delivers its email only after the transaction closed"""
    email_sender = FakeEmailSender()
    transaction_manager = FakeTransactionManager()
    service = build_service(FakeTokenRepository(), email_sender, transaction_manager)

    await service.register_user(CreateUserDTO(email="user@example.com", password="Password123!"))

    assert [email.kind for email in email_sender.sent] == ["activation"]
    assert email_sender.sent[0].inside_transaction is False
    assert transaction_manager.committed == 1


async def test_registration_fails_when_the_activation_token_cannot_be_created():
    """A user is never committed without the token needed to activate it"""
    token_repository = FakeTokenRepository(fail_on_create=TokenCreationError("token storage unavailable"))
    email_sender = FakeEmailSender()
    transaction_manager = FakeTransactionManager()
    service = build_service(token_repository, email_sender, transaction_manager)

    with pytest.raises(UserCreationError) as failure:
        await service.register_user(CreateUserDTO(email="user@example.com", password="Password123!"))

    assert "token" not in str(failure.value).lower()
    assert "database" not in str(failure.value).lower()

    assert transaction_manager.rolled_back == 1
    assert transaction_manager.committed == 0
    assert email_sender.sent == []


async def test_registration_survives_a_failing_email():
    """Delivery failure leaves the account created rather than rolling it back"""
    email_sender = FakeEmailSender(fail=True)
    transaction_manager = FakeTransactionManager()
    service = build_service(FakeTokenRepository(), email_sender, transaction_manager)

    created = await service.register_user(CreateUserDTO(email="user@example.com", password="Password123!"))

    assert created.email == "user@example.com"
    assert transaction_manager.committed == 1


async def test_the_password_is_hashed_outside_the_transaction():
    """Hashing happens before the transaction opens, so no connection waits on it"""
    password_manager = FakePasswordManager()
    transaction_manager = FakeTransactionManager()
    service = AccountService(
        user_repository=FakeUserRepository(),
        user_group_repository=FakeUserGroupRepository(),
        token_repository=FakeTokenRepository(),
        password_manager=password_manager,
        jwt_manager=FakeJWTManager(),
        email_sender=FakeEmailSender(),
        transaction_manager=transaction_manager
    )

    await service.register_user(CreateUserDTO(email="user@example.com", password="Password123!"))

    assert password_manager.hashed_inside_transaction == [False]
    assert transaction_manager.committed == 1
