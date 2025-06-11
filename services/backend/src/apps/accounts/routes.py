"""Routes for accounts module"""

from fastapi import APIRouter, Depends, status

from apps.accounts.controllers import create_user_controller
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
    INTERNAL_SERVER_ERROR
)
from apps.accounts.schemas.examples.user import (
    CREATE_USER_SUCCESS_RESPONSE,
)
from apps.accounts.schemas.user import CreateUserSchema, CreateUserResponseSchema

API_PATHS: dict[str, str] = {
    "register": "/register",
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
