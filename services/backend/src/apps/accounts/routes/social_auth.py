"""
Routes for social authentication API.
"""

from fastapi import APIRouter, Depends, status

from apps.accounts.controllers.social_auth import (
    social_auth_controller,
    get_supported_providers_controller
)
from apps.accounts.services.social_auth.dependencies import get_google_social_auth_service
from oauth.dependencies import get_oauth_registry
from apps.accounts.schemas.social_auth import (
    SocialAuthRequestSchema,
    SocialAuthResponseSchema,
    SupportedProvidersSchema
)
from apps.accounts.schemas.examples.social_auth import (
    SOCIAL_AUTH_REQUEST_GOOGLE,
    SOCIAL_AUTH_REQUEST_FACEBOOK,
    SOCIAL_AUTH_SUCCESS_EXISTING_USER,
    SOCIAL_AUTH_SUCCESS_NEW_USER,
    SUPPORTED_PROVIDERS_RESPONSE,
    SOCIAL_TOKEN_ERROR,
    SOCIAL_PROVIDER_ERROR,
    SOCIAL_USER_INFO_ERROR,
    SOCIAL_USER_VALIDATION_ERROR,
    GOOGLE_EMAIL_NOT_VERIFIED_ERROR,
    PROVIDER_EMPTY_ERROR,
    PROVIDER_UNSUPPORTED_ERROR,
    ACCESS_TOKEN_EMPTY_ERROR,
    EMAIL_INVALID_FORMAT_ERROR
)
from apps.accounts.services.social_auth.interfaces import SocialAuthServiceInterface
from oauth.factories import OAuthProviderRegistry

API_PATHS = {
    "social_auth": "/social-auth",
    "supported_providers": "/social-auth/providers"
}

router = APIRouter(prefix="/auth", tags=["Social Authentication"])


@router.post(
    API_PATHS["social_auth"],
    response_model=SocialAuthResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Authenticate user via social OAuth provider",
    description=(
            "<h3>This endpoint authenticates users through OAuth social providers (Google, Facebook, etc.). "
            "The frontend must first obtain an access token from the OAuth provider and then send it to this endpoint. "
            "Upon successful authentication, the user will receive JWT tokens for accessing the application. "
            "If the user doesn't exist, a new account will be created automatically.</h3>"
    ),
    responses={
        200: {
            "description": "Authentication successful",
            "content": {
                "application/json": {
                    "examples": {
                        "existing_user": {
                            "summary": "Existing user authentication",
                            "description": "User already exists in the system",
                            "value": SOCIAL_AUTH_SUCCESS_EXISTING_USER
                        },
                        "new_user": {
                            "summary": "New user registration",
                            "description": "New user account created and authenticated",
                            "value": SOCIAL_AUTH_SUCCESS_NEW_USER
                        }
                    }
                }
            }
        },
        400: {
            "description": "Validation or user data error",
            "content": {
                "application/json": {
                    "examples": {
                        "user_validation_error": {
                            "summary": "User validation failed",
                            "description": "Required user data is missing or invalid",
                            "value": SOCIAL_USER_VALIDATION_ERROR
                        },
                        "google_email_not_verified": {
                            "summary": "Google email not verified",
                            "description": "Google email must be verified for authentication",
                            "value": GOOGLE_EMAIL_NOT_VERIFIED_ERROR
                        }
                    }
                }
            }
        },
        401: {
            "description": "Token verification failed",
            "content": {
                "application/json": {
                    "examples": {
                        "invalid_token": {
                            "summary": "Invalid access token",
                            "description": "OAuth access token is invalid or expired",
                            "value": SOCIAL_TOKEN_ERROR
                        }
                    }
                }
            }
        },
        422: {
            "description": "Request validation error or user info extraction failed",
            "content": {
                "application/json": {
                    "examples": {
                        "provider_empty": {
                            "summary": "Provider name empty",
                            "description": "OAuth provider name is required",
                            "value": PROVIDER_EMPTY_ERROR
                        },
                        "provider_unsupported": {
                            "summary": "Unsupported provider",
                            "description": "OAuth provider is not supported",
                            "value": PROVIDER_UNSUPPORTED_ERROR
                        },
                        "token_empty": {
                            "summary": "Access token empty",
                            "description": "OAuth access token is required",
                            "value": ACCESS_TOKEN_EMPTY_ERROR
                        },
                        "user_info_error": {
                            "summary": "User info extraction failed",
                            "description": "Failed to extract required user information from OAuth provider",
                            "value": SOCIAL_USER_INFO_ERROR
                        },
                        "email_invalid": {
                            "summary": "Invalid email format",
                            "description": "Email address format validation failed",
                            "value": EMAIL_INVALID_FORMAT_ERROR
                        }
                    }
                }
            }
        },
        503: {
            "description": "OAuth provider service unavailable",
            "content": {
                "application/json": {
                    "examples": {
                        "provider_unavailable": {
                            "summary": "Provider service error",
                            "description": "OAuth provider service is temporarily unavailable",
                            "value": SOCIAL_PROVIDER_ERROR
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
                        "configuration_error": {
                            "summary": "Configuration error",
                            "description": "OAuth provider configuration is invalid",
                            "value": {
                                "success": False,
                                "error_type": "SocialConfigurationError",
                                "error_message": "Service configuration error",
                                "provider": "google",
                                "details": {"timestamp": "2024-06-24T12:00:00Z"}
                            }
                        },
                        "database_error": {
                            "summary": "Database error",
                            "description": "Database error during user processing",
                            "value": {
                                "success": False,
                                "error_type": "SocialUserLookupError",
                                "error_message": "Database error during user processing",
                                "provider": "facebook",
                                "details": {"timestamp": "2024-06-24T12:00:00Z"}
                            }
                        },
                        "token_generation_error": {
                            "summary": "Token generation failed",
                            "description": "Failed to generate JWT tokens",
                            "value": {
                                "success": False,
                                "error_type": "SocialTokenGenerationError",
                                "error_message": "Failed to generate authentication tokens",
                                "provider": "github",
                                "details": {"timestamp": "2024-06-24T12:00:00Z"}
                            }
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
                        "google_auth": {
                            "summary": "Google authentication",
                            "description": "Example of Google OAuth authentication request",
                            "value": SOCIAL_AUTH_REQUEST_GOOGLE
                        },
                        "facebook_auth": {
                            "summary": "Facebook authentication",
                            "description": "Example of Facebook OAuth authentication request",
                            "value": SOCIAL_AUTH_REQUEST_FACEBOOK
                        }
                    }
                }
            }
        }
    }
)
async def social_auth_route(
        request_data: SocialAuthRequestSchema,
        social_auth_service: SocialAuthServiceInterface = Depends(get_google_social_auth_service)
) -> SocialAuthResponseSchema:
    """
    Authenticate user via social OAuth provider

    Args:
        request_data: Social authentication request data (provider and access token)
        social_auth_service: Social authentication service for business logic

    Returns:
        SocialAuthResponseSchema: Authentication result with JWT tokens and user profile

    Raises:
        HTTPException:
            - 400 for validation or user data errors
            - 401 for invalid/expired OAuth tokens
            - 422 for request validation or user info extraction errors
            - 503 for OAuth provider service unavailability
            - 500 for internal server errors (configuration, database, token generation)
    """
    return await social_auth_controller(
        request_data=request_data,
        social_auth_service=social_auth_service
    )


@router.get(
    API_PATHS["supported_providers"],
    response_model=SupportedProvidersSchema,
    status_code=status.HTTP_200_OK,
    summary="Get list of supported OAuth providers",
    description=(
            "<h3>This endpoint returns the list of OAuth providers supported by the application. "
            "Use this information to determine which social authentication options are available to users. "
            "The response includes provider names and the total count.</h3>"
    ),
    responses={
        200: {
            "description": "List of supported providers",
            "content": {
                "application/json": {
                    "examples": {
                        "supported_providers": {
                            "summary": "Supported OAuth providers",
                            "description": "List of all available OAuth providers",
                            "value": SUPPORTED_PROVIDERS_RESPONSE
                        }
                    }
                }
            }
        }
    }
)
async def get_supported_providers_route(
        registry: OAuthProviderRegistry = Depends(get_oauth_registry)
) -> SupportedProvidersSchema:
    """
    Get list of supported OAuth providers

    Args:
        registry: OAuth provider registry for getting supported providers

    Returns:
        SupportedProvidersSchema: List of supported OAuth providers and total count

    Note:
        This endpoint never fails and always returns at least one provider
    """
    return await get_supported_providers_controller(registry)
