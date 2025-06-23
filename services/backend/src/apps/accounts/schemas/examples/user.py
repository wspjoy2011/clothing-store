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

LOGIN_RESPONSE_EXAMPLE = {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c",
    "refresh_token": "def50200e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855ae41e4649b934ca495991b7852b855",
    "token_type": "bearer"
}

USER_LOGIN_REQUEST_EXAMPLE = {
    "email": "john.doe@example.com",
    "password": "SecurePass123!"
}

REFRESH_TOKEN_REQUEST_EXAMPLE = {
    "refresh_token": "def50200e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855ae41e4649b934ca495991b7852b855"
}

REFRESH_TOKEN_SUCCESS_RESPONSE = {
    "user": USER_RESPONSE_EXAMPLE,
    "message": "User retrieved successfully"
}

GET_USER_BY_TOKEN_SUCCESS_RESPONSE = {
    "user": USER_RESPONSE_EXAMPLE,
    "message": "User retrieved successfully"
}
