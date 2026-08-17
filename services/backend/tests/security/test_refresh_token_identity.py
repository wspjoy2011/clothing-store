import pytest

from security.exceptions import InvalidTokenTypeError
from security.jwt_token import JWTManager

PAYLOAD = {"user_id": 1, "email": "user@example.com", "group_id": 1, "group_name": "user"}


def build_manager(shared_secret: bool = False) -> JWTManager:
    """
    Build a JWT manager with test secrets

    Args:
        shared_secret: Sign both kinds with one secret, so the signature check
            passes and the type claim is what decides

    Returns:
        Manager issuing tokens for these tests
    """
    return JWTManager(
        access_secret="shared-secret" if shared_secret else "access-secret",
        refresh_secret="shared-secret" if shared_secret else "refresh-secret",
        algorithm="HS256",
        access_expire_minutes=30,
        refresh_expire_minutes=10080
    )


def test_two_refresh_tokens_of_one_user_are_different():
    """Issuing twice within the same second still yields two distinct tokens"""
    manager = build_manager()

    first = manager.create_refresh_token(PAYLOAD)
    second = manager.create_refresh_token(PAYLOAD)

    assert first != second


def test_a_refresh_token_carries_an_identifier():
    """The identifier is what makes one issued token distinguishable from the next"""
    manager = build_manager()

    payload = manager.verify_refresh_token(manager.create_refresh_token(PAYLOAD))

    assert payload["jti"]


def test_the_identifier_differs_between_issues():
    """Two tokens of the same user carry different identifiers"""
    manager = build_manager()

    first = manager.verify_refresh_token(manager.create_refresh_token(PAYLOAD))
    second = manager.verify_refresh_token(manager.create_refresh_token(PAYLOAD))

    assert first["jti"] != second["jti"]


def test_a_refresh_token_still_carries_the_user_it_belongs_to():
    """Adding the identifier did not displace the payload the service reads"""
    manager = build_manager()

    payload = manager.verify_refresh_token(manager.create_refresh_token(PAYLOAD))

    assert payload["user_id"] == PAYLOAD["user_id"]
    assert payload["type"] == "refresh"


def test_an_access_token_is_refused_by_the_refresh_check():
    """The type claim is enforced, and its refusal is not repackaged as a surprise"""
    manager = build_manager(shared_secret=True)

    access_token = manager.create_access_token(PAYLOAD)

    with pytest.raises(InvalidTokenTypeError):
        manager.verify_refresh_token(access_token)


def test_a_refresh_token_is_refused_by_the_access_check():
    """The same holds in the other direction"""
    manager = build_manager(shared_secret=True)

    refresh_token = manager.create_refresh_token(PAYLOAD)

    with pytest.raises(InvalidTokenTypeError):
        manager.verify_access_token(refresh_token)
