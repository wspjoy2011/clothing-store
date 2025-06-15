"""Examples for activation schemas for API documentation"""

ACTIVATE_ACCOUNT_REQUEST_EXAMPLE = {
    "email": "john.doe@example.com",
    "token": "AbCdEf123456789XyZ-_TokenExample123"
}

RESEND_ACTIVATION_REQUEST_EXAMPLE = {
    "email": "john.doe@example.com"
}

ACTIVATE_ACCOUNT_SUCCESS_RESPONSE = {
    "user": {
        "id": 1,
        "email": "john.doe@example.com",
        "is_active": True,
        "created_at": "2025-06-10T10:30:00.123456+00:00",
        "updated_at": "2025-06-15T14:45:30.987654+00:00",
        "group_id": 1,
        "group_name": "user"
    },
    "message": "Account activated successfully"
}

ACTIVATION_STATUS_ACTIVE_RESPONSE = {
    "email": "john.doe@example.com",
    "is_active": True,
    "requires_activation": False,
    "message": "Account is already active"
}

ACTIVATION_STATUS_INACTIVE_RESPONSE = {
    "email": "jane.smith@example.com",
    "is_active": False,
    "requires_activation": True,
    "message": "Account requires activation"
}

RESEND_ACTIVATION_SUCCESS_RESPONSE = {
    "message": "Activation email sent successfully",
    "email": "john.doe@example.com"
}

ACTIVATION_USER_NOT_FOUND_ERROR = {
    "detail": "User with email 'unknown@example.com' not found"
}

ACTIVATION_ALREADY_ACTIVE_ERROR = {
    "detail": "User with email 'john.doe@example.com' is already activated"
}

ACTIVATION_INVALID_TOKEN_ERROR = {
    "detail": "Invalid email and token combination"
}

ACTIVATION_EXPIRED_TOKEN_ERROR = {
    "detail": "Activation token has expired"
}

ACTIVATION_VALIDATION_ERROR = {
    "field": "token",
    "message": "Token is too short"
}

ACTIVATION_TOKEN_EXAMPLES = [
    "AbCdEf123456789XyZ-_TokenExample123",
    "Xy9ZpQ8rM7nB6vC5xW4e3R2t1Y0uI9oP",
    "aB3cD4eF5gH6iJ7kL8mN9oP0qR1sT2uV",
    "zY8xW7vU6tS5rQ4pO3nM2lK1jI0hG9fE"
]

ACTIVATION_EMAIL_EXAMPLES = [
    "user@example.com",
    "test.user+tag@domain.co.uk",
    "firstname.lastname@company.org",
    "admin@subdomain.example.net"
]

ACTIVATION_WORKFLOW_EXAMPLES = {
    "registration_response": {
        "user": {
            "id": 1,
            "email": "newuser@example.com",
            "is_active": False,
            "created_at": "2025-06-15T10:00:00.000000+00:00",
            "updated_at": "2025-06-15T10:00:00.000000+00:00",
            "group_id": 1,
            "group_name": "user"
        },
        "message": "User created successfully"
    },
    "activation_request": {
        "email": "newuser@example.com",
        "token": "aB3cD4eF5gH6iJ7kL8mN9oP0qR1sT2uV"
    },
    "activation_response": {
        "user": {
            "id": 1,
            "email": "newuser@example.com",
            "is_active": True,
            "created_at": "2025-06-15T10:00:00.000000+00:00",
            "updated_at": "2025-06-15T10:05:30.123456+00:00",
            "group_id": 1,
            "group_name": "user"
        },
        "message": "Account activated successfully"
    }
}

ACTIVATION_RATE_LIMIT_ERROR = {
    "detail": "Too many activation attempts. Please try again later."
}

RESEND_RATE_LIMIT_ERROR = {
    "detail": "Activation email was already sent recently. Please check your inbox or try again later."
}
