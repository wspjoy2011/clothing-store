"""Examples for user schemas for API documentation"""

CREATE_USER_REQUEST_EXAMPLE = {
    "email": "john.doe@example.com",
    "password": "SecurePass123!"
}

USER_RESPONSE_EXAMPLE = {
    "id": 1,
    "email": "john.doe@example.com",
    "is_active": True,
    "created_at": "2025-06-10T10:30:00.123456+00:00",
    "updated_at": "2025-06-10T10:30:00.123456+00:00",
    "group_id": 1,
    "group_name": "user"
}

CREATE_USER_SUCCESS_RESPONSE = {
    "user": USER_RESPONSE_EXAMPLE,
    "message": "User created successfully"
}
