from security.jwt_token import JWTManager

PAYLOAD = {"user_id": 1, "email": "user@example.com", "group_id": 1, "group_name": "user"}


def build_manager() -> JWTManager:
    """
    Build a JWT manager with test secrets

    Returns:
        Manager issuing tokens for these tests
    """
    return JWTManager(
        access_secret="access-secret",
        refresh_secret="refresh-secret",
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
