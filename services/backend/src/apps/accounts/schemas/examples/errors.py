EMAIL_VALIDATION_ERROR = {
    "field": "email",
    "message": "value is not a valid email address"
}

PASSWORD_EMPTY_ERROR = {
    "field": "password",
    "message": "ensure this value has at least 1 characters"
}

PASSWORD_TOO_SHORT_ERROR = {
    "field": "password",
    "message": "Password must be at least 8 characters long"
}

PASSWORD_NO_UPPERCASE_ERROR = {
    "field": "password",
    "message": "Password must contain at least one uppercase letter"
}

PASSWORD_NO_LOWERCASE_ERROR = {
    "field": "password",
    "message": "Password must contain at least one lowercase letter"
}

PASSWORD_NO_DIGIT_ERROR = {
    "field": "password",
    "message": "Password must contain at least one digit"
}

PASSWORD_NO_SPECIAL_CHAR_ERROR = {
    "field": "password",
    "message": "Password must contain at least one special character"
}

PASSWORD_TOO_LONG_ERROR = {
    "field": "password",
    "message": "Password must be no more than 128 characters long"
}

EMAIL_ALREADY_EXISTS_ERROR = {
    "detail": "User with email 'john.doe@example.com' already exists"
}

USER_CREATION_ERROR = {
    "detail": "Failed to create user: Database constraint violation"
}

PASSWORD_PROCESSING_ERROR = {
    "detail": "Password processing failed: Invalid password format"
}

INTERNAL_SERVER_ERROR = {
    "detail": "Internal server error occurred during user creation"
}
