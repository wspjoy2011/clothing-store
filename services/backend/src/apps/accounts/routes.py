"""Routes for accounts module"""

from fastapi import APIRouter, Depends, status

from apps.accounts.controllers import (
    create_user_controller,
    activate_account_controller,
    resend_activation_controller,
    login_user_controller,
    logout_user_controller,
    get_user_by_refresh_token_controller
)
from apps.accounts.dependencies import get_account_service
from apps.accounts.interfaces.services import AccountServiceInterface
from apps.accounts.schemas.examples.errors import (
    EMAIL_ALREADY_EXISTS_ERROR,
    USER_CREATION_ERROR,
    PASSWORD_PROCESSING_ERROR,
    EMAIL_VALIDATION_ERROR,
    PASSWORD_EMPTY_ERROR,
    PASSWORD_TOO_SHORT_ERROR,
    PASSWORD_NO_UPPERCASE_ERROR,
    PASSWORD_NO_LOWERCASE_ERROR,
    PASSWORD_NO_DIGIT_ERROR,
    PASSWORD_NO_SPECIAL_CHAR_ERROR,
    PASSWORD_TOO_LONG_ERROR,
    INTERNAL_SERVER_ERROR,
    INVALID_CREDENTIALS_ERROR,
    USER_INACTIVE_ERROR,
    USER_NOT_FOUND_ERROR,
    TOKEN_GENERATION_ERROR,
    LOGIN_ERROR,
    AUTHORIZATION_HEADER_MISSING_ERROR,
    INVALID_AUTHORIZATION_HEADER_ERROR,
    INVALID_REFRESH_TOKEN_ERROR,
    REFRESH_TOKEN_NOT_FOUND_ERROR,
    REFRESH_TOKEN_EXPIRED_ERROR,
    TOKEN_VALIDATION_ERROR
)
from apps.accounts.schemas.examples.user import (
    CREATE_USER_SUCCESS_RESPONSE,
    LOGIN_RESPONSE_EXAMPLE,
    USER_LOGIN_REQUEST_EXAMPLE,
    GET_USER_BY_TOKEN_SUCCESS_RESPONSE
)
from apps.accounts.schemas.examples.activation import (
    ACTIVATE_ACCOUNT_REQUEST_EXAMPLE,
    ACTIVATE_ACCOUNT_SUCCESS_RESPONSE,
    RESEND_ACTIVATION_REQUEST_EXAMPLE,
    RESEND_ACTIVATION_SUCCESS_RESPONSE,
    ACTIVATION_USER_NOT_FOUND_ERROR,
    ACTIVATION_ALREADY_ACTIVE_ERROR,
    ACTIVATION_INVALID_TOKEN_ERROR,
    ACTIVATION_EXPIRED_TOKEN_ERROR,
    ACTIVATION_VALIDATION_ERROR,
    RESEND_ALREADY_ACTIVE_ERROR,
    RESEND_USER_NOT_FOUND_ERROR,
    RESEND_RATE_LIMIT_ERROR
)
from apps.accounts.schemas.user import (
    CreateUserSchema,
    CreateUserResponseSchema,
    LoginResponseSchema,
    UserLoginSchema,
    LogoutResponseSchema,
    LogoutSchema,
    RefreshTokenResponseSchema
)
from apps.accounts.schemas.activation import (
    ActivateAccountSchema,
    ActivateAccountResponseSchema,
    ResendActivationSchema,
    ResendActivationResponseSchema
)
from security.http import JWTTokenDependency

API_PATHS: dict[str, str] = {
    "register": "/register",
    "login": "/login",
    "logout": "/logout",
    "activate": "/activate",
    "resend_activation": "/resend-activation",
    "me": "/me",
}

router = APIRouter(
    prefix="/accounts",
    tags=["accounts"]
)


@router.post(
    API_PATHS["register"],
    response_model=CreateUserResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description=(
            "<h3>This endpoint allows registration of a new user account. "
            "The user will be automatically assigned to the 'user' group and will have "
            "an inactive status until account activation. "
            "Password must meet security requirements: minimum 8 characters with "
            "uppercase, lowercase, digit, and special character.</h3>"
    ),
    responses={
        201: {
            "description": "User created successfully",
            "content": {
                "application/json": {
                    "example": CREATE_USER_SUCCESS_RESPONSE
                }
            }
        },
        400: {
            "description": "Business logic error (email exists, creation failed, password processing error)",
            "content": {
                "application/json": {
                    "examples": {
                        "email_already_exists": {
                            "summary": "Email already exists",
                            "description": "User with this email already exists in the system",
                            "value": EMAIL_ALREADY_EXISTS_ERROR
                        },
                        "user_creation_error": {
                            "summary": "User creation failed",
                            "description": "Database or repository level error during user creation",
                            "value": USER_CREATION_ERROR
                        },
                        "password_processing_error": {
                            "summary": "Password processing error",
                            "description": "Error during password hashing or validation",
                            "value": PASSWORD_PROCESSING_ERROR
                        }
                    }
                }
            }
        },
        422: {
            "description": "Request validation error (handled by main.py custom exception handler)",
            "content": {
                "application/json": {
                    "examples": {
                        "invalid_email": {
                            "summary": "Invalid email format",
                            "description": "Email address format validation failed",
                            "value": EMAIL_VALIDATION_ERROR
                        },
                        "password_empty": {
                            "summary": "Empty password",
                            "description": "Password field is empty or missing",
                            "value": PASSWORD_EMPTY_ERROR
                        },
                        "password_too_short": {
                            "summary": "Password too short",
                            "description": "Password must be at least 8 characters",
                            "value": PASSWORD_TOO_SHORT_ERROR
                        },
                        "password_no_uppercase": {
                            "summary": "No uppercase letter",
                            "description": "Password must contain at least one uppercase letter",
                            "value": PASSWORD_NO_UPPERCASE_ERROR
                        },
                        "password_no_lowercase": {
                            "summary": "No lowercase letter",
                            "description": "Password must contain at least one lowercase letter",
                            "value": PASSWORD_NO_LOWERCASE_ERROR
                        },
                        "password_no_digit": {
                            "summary": "No digit",
                            "description": "Password must contain at least one digit",
                            "value": PASSWORD_NO_DIGIT_ERROR
                        },
                        "password_no_special_char": {
                            "summary": "No special character",
                            "description": "Password must contain at least one special character",
                            "value": PASSWORD_NO_SPECIAL_CHAR_ERROR
                        },
                        "password_too_long": {
                            "summary": "Password too long",
                            "description": "Password must be no more than 128 characters",
                            "value": PASSWORD_TOO_LONG_ERROR
                        }
                    }
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": INTERNAL_SERVER_ERROR
                }
            }
        }
    }
)
async def register_user_route(
        user_data: CreateUserSchema,
        account_service: AccountServiceInterface = Depends(get_account_service)
) -> CreateUserResponseSchema:
    """
    Register a new user account

    Args:
        user_data: User registration data (email and password)
        account_service: Account service for business logic

    Returns:
        CreateUserResponseSchema: Created user data with success message

    Raises:
        HTTPException:
            - 400 for validation errors or password requirements
            - 409 if email already exists
            - 500 for internal server errors
    """
    return await create_user_controller(
        user_data=user_data,
        account_service=account_service
    )


@router.post(
    API_PATHS["activate"],
    response_model=ActivateAccountResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Activate user account",
    description=(
            "<h3>This endpoint activates a user account using the activation token sent via email. "
            "The token must be valid and not expired. After successful activation, "
            "the user's status will be set to active and they will be able to log in. "
            "The activation token will be automatically deleted after use.</h3>"
    ),
    responses={
        200: {
            "description": "Account activated successfully",
            "content": {
                "application/json": {
                    "example": ACTIVATE_ACCOUNT_SUCCESS_RESPONSE
                }
            }
        },
        400: {
            "description": "Activation error (already activated, invalid token)",
            "content": {
                "application/json": {
                    "examples": {
                        "already_activated": {
                            "summary": "User already activated",
                            "description": "User account is already in active status",
                            "value": ACTIVATION_ALREADY_ACTIVE_ERROR
                        },
                        "invalid_token": {
                            "summary": "Invalid activation token",
                            "description": "Email and token combination is not valid",
                            "value": ACTIVATION_INVALID_TOKEN_ERROR
                        }
                    }
                }
            }
        },
        404: {
            "description": "User not found",
            "content": {
                "application/json": {
                    "examples": {
                        "user_not_found": {
                            "summary": "User not found",
                            "description": "No user found with the provided email address",
                            "value": ACTIVATION_USER_NOT_FOUND_ERROR
                        }
                    }
                }
            }
        },
        410: {
            "description": "Activation token expired",
            "content": {
                "application/json": {
                    "examples": {
                        "token_expired": {
                            "summary": "Token expired",
                            "description": "Activation token has expired and cannot be used",
                            "value": ACTIVATION_EXPIRED_TOKEN_ERROR
                        }
                    }
                }
            }
        },
        422: {
            "description": "Request validation error",
            "content": {
                "application/json": {
                    "examples": {
                        "invalid_email": {
                            "summary": "Invalid email format",
                            "description": "Email address format validation failed",
                            "value": EMAIL_VALIDATION_ERROR
                        },
                        "invalid_token": {
                            "summary": "Invalid token format",
                            "description": "Token format validation failed",
                            "value": ACTIVATION_VALIDATION_ERROR
                        }
                    }
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": INTERNAL_SERVER_ERROR
                }
            }
        }
    },
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "examples": {
                        "activation_request": {
                            "summary": "Account activation request",
                            "description": "Example of activation request with email and token",
                            "value": ACTIVATE_ACCOUNT_REQUEST_EXAMPLE
                        }
                    }
                }
            }
        }
    }
)
async def activate_account_route(
        activation_data: ActivateAccountSchema,
        account_service: AccountServiceInterface = Depends(get_account_service)
) -> ActivateAccountResponseSchema:
    """
    Activate user account with email and token

    Args:
        activation_data: Account activation data (email and token)
        account_service: Account service for business logic

    Returns:
        ActivateAccountResponseSchema: Activated user data with success message

    Raises:
        HTTPException:
            - 400 if user already activated or token invalid
            - 404 if user not found
            - 410 if token expired
            - 422 for validation errors
            - 500 for internal server errors
    """
    return await activate_account_controller(
        activation_data=activation_data,
        account_service=account_service
    )


@router.post(
    API_PATHS["resend_activation"],
    response_model=ResendActivationResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Resend activation email",
    description=(
            "<h3>This endpoint resends the activation email to a user who has not yet activated their account. "
            "A new activation token will be generated and the old one will be invalidated for security. "
            "The endpoint will only work for users who are registered but not yet activated. "
            "Rate limiting may apply to prevent abuse.</h3>"
    ),
    responses={
        200: {
            "description": "Activation email sent successfully",
            "content": {
                "application/json": {
                    "example": RESEND_ACTIVATION_SUCCESS_RESPONSE
                }
            }
        },
        400: {
            "description": "User already activated or other business logic error",
            "content": {
                "application/json": {
                    "examples": {
                        "already_activated": {
                            "summary": "User already activated",
                            "description": "User account is already in active status and doesn't need reactivation",
                            "value": RESEND_ALREADY_ACTIVE_ERROR
                        },
                        "rate_limit": {
                            "summary": "Rate limit exceeded",
                            "description": "Activation email was sent recently, please wait before requesting again",
                            "value": RESEND_RATE_LIMIT_ERROR
                        }
                    }
                }
            }
        },
        404: {
            "description": "User not found",
            "content": {
                "application/json": {
                    "examples": {
                        "user_not_found": {
                            "summary": "User not found",
                            "description": "No user found with the provided email address",
                            "value": RESEND_USER_NOT_FOUND_ERROR
                        }
                    }
                }
            }
        },
        422: {
            "description": "Request validation error",
            "content": {
                "application/json": {
                    "examples": {
                        "invalid_email": {
                            "summary": "Invalid email format",
                            "description": "Email address format validation failed",
                            "value": EMAIL_VALIDATION_ERROR
                        }
                    }
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": INTERNAL_SERVER_ERROR
                }
            }
        }
    },
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "examples": {
                        "resend_activation_request": {
                            "summary": "Resend activation email request",
                            "description": "Example of resend activation request with email only",
                            "value": RESEND_ACTIVATION_REQUEST_EXAMPLE
                        }
                    }
                }
            }
        }
    }
)
async def resend_activation_route(
        resend_data: ResendActivationSchema,
        account_service: AccountServiceInterface = Depends(get_account_service)
) -> ResendActivationResponseSchema:
    """
    Resend activation email to user

    Args:
        resend_data: Resend activation data (email only)
        account_service: Account service for business logic

    Returns:
        ResendActivationResponseSchema: Success message with email confirmation

    Raises:
        HTTPException:
            - 400 if user already activated or rate limit exceeded
            - 404 if user not found
            - 422 for validation errors
            - 500 for internal server errors
    """
    return await resend_activation_controller(
        resend_data=resend_data,
        account_service=account_service
    )


@router.post(
    API_PATHS["login"],
    response_model=LoginResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Login user",
    description=(
            "<h3>This endpoint authenticates a user and returns JWT tokens for API access. "
            "The user account must be activated before login is allowed. "
            "Returns access token for API requests and refresh token for token renewal. "
            "Both tokens should be stored securely on the client side.</h3>"
    ),
    responses={
        200: {
            "description": "Login successful",
            "content": {
                "application/json": {
                    "example": LOGIN_RESPONSE_EXAMPLE
                }
            }
        },
        401: {
            "description": "Invalid credentials",
            "content": {
                "application/json": {
                    "examples": {
                        "invalid_credentials": {
                            "summary": "Invalid email or password",
                            "description": "The provided email and password combination is incorrect",
                            "value": INVALID_CREDENTIALS_ERROR
                        }
                    }
                }
            }
        },
        403: {
            "description": "User account not activated",
            "content": {
                "application/json": {
                    "examples": {
                        "user_inactive": {
                            "summary": "User account not activated",
                            "description": "User account exists but is not activated via email",
                            "value": USER_INACTIVE_ERROR
                        }
                    }
                }
            }
        },
        404: {
            "description": "User not found",
            "content": {
                "application/json": {
                    "examples": {
                        "user_not_found": {
                            "summary": "User not found",
                            "description": "No user found with the provided email address",
                            "value": USER_NOT_FOUND_ERROR
                        }
                    }
                }
            }
        },
        422: {
            "description": "Request validation error",
            "content": {
                "application/json": {
                    "examples": {
                        "invalid_email": {
                            "summary": "Invalid email format",
                            "description": "Email address format validation failed",
                            "value": EMAIL_VALIDATION_ERROR
                        },
                        "password_empty": {
                            "summary": "Empty password",
                            "description": "Password field is empty or missing",
                            "value": PASSWORD_EMPTY_ERROR
                        }
                    }
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "examples": {
                        "token_generation_error": {
                            "summary": "Token generation failed",
                            "description": "Failed to generate JWT tokens during login",
                            "value": TOKEN_GENERATION_ERROR
                        },
                        "login_error": {
                            "summary": "Login processing error",
                            "description": "Unexpected error occurred during login process",
                            "value": LOGIN_ERROR
                        },
                        "internal_server_error": {
                            "summary": "General server error",
                            "description": "Internal server error occurred during login",
                            "value": INTERNAL_SERVER_ERROR
                        }
                    }
                }
            }
        }
    },
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "examples": {
                        "login_request": {
                            "summary": "User login request",
                            "description": "Example of login request with email and password",
                            "value": USER_LOGIN_REQUEST_EXAMPLE
                        }
                    }
                }
            }
        }
    }
)
async def login_user_route(
        login_data: UserLoginSchema,
        account_service: AccountServiceInterface = Depends(get_account_service)
) -> LoginResponseSchema:
    """
    Authenticate user and return JWT tokens

    Args:
        login_data: User login credentials (email and password)
        account_service: Account service for business logic

    Returns:
        LoginResponseSchema: JWT access and refresh tokens

    Raises:
        HTTPException:
            - 401 for invalid credentials
            - 403 if user account not activated
            - 404 if user not found
            - 422 for validation errors
            - 500 for server errors
    """
    return await login_user_controller(
        login_data=login_data,
        account_service=account_service
    )


@router.post(
    API_PATHS["logout"],
    response_model=LogoutResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Logout user",
    description=(
            "<h3>This endpoint logs out a user by invalidating their refresh token. "
            "After logout, the refresh token can no longer be used to generate new access tokens. "
            "This endpoint always returns success, even if the token doesn't exist in the database.</h3>"
    ),
    responses={
        200: {
            "description": "Logout successful",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Logout successful"
                    }
                }
            }
        }
    },
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "examples": {
                        "logout_request": {
                            "summary": "User logout request",
                            "description": "Example of logout request with refresh token",
                            "value": {
                                "refresh_token": "def50200e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855ae41e4649b934ca495991b7852b855"
                            }
                        }
                    }
                }
            }
        }
    }
)
async def logout_user_route(
        logout_data: LogoutSchema,
        account_service: AccountServiceInterface = Depends(get_account_service)
) -> LogoutResponseSchema:
    """
    Logout user by invalidating refresh token

    Args:
        logout_data: User logout data (refresh token)
        account_service: Account service for business logic

    Returns:
        LogoutResponseSchema: Success message

    Note:
        This endpoint never fails - always returns success
    """
    return await logout_user_controller(
        logout_data=logout_data,
        account_service=account_service
    )


@router.get(
    API_PATHS["me"],
    response_model=RefreshTokenResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Get current user by refresh token",
    description=(
            "<h3>This endpoint retrieves current user information using a refresh token from Authorization header. "
            "The refresh token must be valid, not expired, and present in the database. "
            "Use this endpoint to get user details when you have a refresh token but need user information. "
            "The token must be provided in Authorization header as 'Bearer {refresh_token}'.</h3>"
    ),
    responses={
        200: {
            "description": "User retrieved successfully",
            "content": {
                "application/json": {
                    "example": GET_USER_BY_TOKEN_SUCCESS_RESPONSE
                }
            }
        },
        401: {
            "description": "Unauthorized - Invalid or expired refresh token",
            "content": {
                "application/json": {
                    "examples": {
                        "missing_header": {
                            "summary": "Authorization header missing",
                            "description": "Authorization header is not provided in the request",
                            "value": AUTHORIZATION_HEADER_MISSING_ERROR
                        },
                        "invalid_header_format": {
                            "summary": "Invalid Authorization header format",
                            "description": "Authorization header format is incorrect (should be 'Bearer <token>')",
                            "value": INVALID_AUTHORIZATION_HEADER_ERROR
                        },
                        "invalid_refresh_token": {
                            "summary": "Invalid or expired refresh token",
                            "description": "Refresh token is invalid, malformed, or has expired",
                            "value": INVALID_REFRESH_TOKEN_ERROR
                        },
                        "token_not_found": {
                            "summary": "Refresh token not found",
                            "description": "Refresh token not found in database or has been revoked",
                            "value": REFRESH_TOKEN_NOT_FOUND_ERROR
                        },
                        "token_expired": {
                            "summary": "Refresh token expired",
                            "description": "Refresh token has expired and cannot be used",
                            "value": REFRESH_TOKEN_EXPIRED_ERROR
                        },
                        "token_validation_error": {
                            "summary": "Token validation error",
                            "description": "Token payload is invalid or missing required fields",
                            "value": TOKEN_VALIDATION_ERROR
                        }
                    }
                }
            }
        },
        404: {
            "description": "User not found",
            "content": {
                "application/json": {
                    "examples": {
                        "user_not_found": {
                            "summary": "User not found",
                            "description": "User associated with the refresh token no longer exists",
                            "value": USER_NOT_FOUND_ERROR
                        }
                    }
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": INTERNAL_SERVER_ERROR
                }
            }
        }
    }
)
async def get_user_by_refresh_token_route(
        refresh_token: JWTTokenDependency,
        account_service: AccountServiceInterface = Depends(get_account_service)
) -> RefreshTokenResponseSchema:
    """
    Get current user information by refresh token

    Args:
        refresh_token: JWT refresh token from Authorization header
        account_service: Account service for business logic

    Returns:
        RefreshTokenResponseSchema: User data with success message

    Raises:
        HTTPException:
            - 401 for missing/invalid Authorization header or invalid/expired tokens
            - 404 if user associated with token not found
            - 500 for internal server errors
    """
    return await get_user_by_refresh_token_controller(
        refresh_token=refresh_token,
        account_service=account_service
    )
