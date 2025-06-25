"""
Controllers for social authentication module.
"""

import logging
from dataclasses import asdict
from datetime import datetime, UTC

from fastapi import HTTPException

from apps.accounts.schemas.social_auth import (
    SocialAuthRequestSchema,
    SocialAuthResponseSchema,
    SupportedProvidersSchema
)
from apps.accounts.services.social_auth.interfaces import SocialAuthServiceInterface
from apps.accounts.services.social_auth.dto import SocialAuthRequest
from apps.accounts.services.social_auth.exceptions import (
    SocialAuthError,
    SocialProviderError,
    SocialTokenError,
    SocialUserInfoError,
    SocialUserValidationError,
    SocialConfigurationError,
    SocialUserLookupError,
    SocialTokenGenerationError
)
from oauth.factories import OAuthProviderRegistry

logger = logging.getLogger(__name__)


async def social_auth_controller(
        request_data: SocialAuthRequestSchema,
        social_auth_service: SocialAuthServiceInterface,
) -> SocialAuthResponseSchema:
    """
    Controller for social authentication.

    Args:
        request_data: Social authentication request data
        social_auth_service: Social authentication service

    Returns:
        SocialAuthResponseSchema with authentication result

    Raises:
        HTTPException: Various status codes based on error type
    """
    try:
        auth_request = SocialAuthRequest(
            provider=request_data.provider,
            access_token=request_data.access_token
        )

        auth_response = await social_auth_service.authenticate(auth_request)

        tokens_dict = asdict(auth_response.tokens) if auth_response.tokens else None
        user_profile_dict = asdict(auth_response.user_profile) if auth_response.user_profile else None

        return SocialAuthResponseSchema(
            success=auth_response.success,
            tokens=tokens_dict,
            user_profile=user_profile_dict,
            is_new_user=auth_response.is_new_user,
            message=auth_response.message,
            provider=auth_response.provider
        )

    except SocialTokenError as e:
        logger.warning(f"Social token error: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail={
                "success": False,
                "error_type": "SocialTokenError",
                "error_message": str(e),
                "provider": e.provider,
                "details": {
                    "status_code": getattr(e, 'status_code', 401),
                    "timestamp": datetime.now(UTC).isoformat()
                }
            }
        )

    except SocialUserValidationError as e:
        logger.warning(f"Social user validation error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "error_type": "SocialUserValidationError",
                "error_message": str(e),
                "provider": e.provider,
                "details": {
                    "timestamp": datetime.now(UTC).isoformat()
                }
            }
        )

    except SocialUserInfoError as e:
        logger.warning(f"Social user info error: {str(e)}")
        raise HTTPException(
            status_code=422,
            detail={
                "success": False,
                "error_type": "SocialUserInfoError",
                "error_message": str(e),
                "provider": e.provider,
                "details": {
                    "missing_fields": getattr(e, 'missing_fields', []),
                    "timestamp": datetime.now(UTC).isoformat()
                }
            }
        )

    except SocialProviderError as e:
        logger.error(f"Social provider error: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail={
                "success": False,
                "error_type": "SocialProviderError",
                "error_message": str(e),
                "provider": e.provider,
                "details": {
                    "timestamp": datetime.now(UTC).isoformat()
                }
            }
        )

    except SocialConfigurationError as e:
        logger.error(f"Social configuration error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error_type": "SocialConfigurationError",
                "error_message": "Service configuration error",
                "provider": e.provider,
                "details": {
                    "timestamp": datetime.now(UTC).isoformat()
                }
            }
        )

    except SocialUserLookupError as e:
        logger.error(f"Social user lookup error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error_type": "SocialUserLookupError",
                "error_message": "Database error during user processing",
                "provider": e.provider,
                "details": {
                    "timestamp": datetime.now(UTC).isoformat()
                }
            }
        )

    except SocialTokenGenerationError as e:
        logger.error(f"Social token generation error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error_type": "SocialTokenGenerationError",
                "error_message": "Failed to generate authentication tokens",
                "provider": e.provider,
                "details": {
                    "timestamp": datetime.now(UTC).isoformat()
                }
            }
        )

    except SocialAuthError as e:
        logger.error(f"General social auth error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error_type": "SocialAuthError",
                "error_message": "Authentication failed",
                "provider": e.provider,
                "details": {
                    "timestamp": datetime.now(UTC).isoformat()
                }
            }
        )

    except Exception as e:
        logger.error(f"Unexpected error in social auth: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error_type": "InternalServerError",
                "error_message": "Internal server error occurred during authentication",
                "provider": request_data.provider,
                "details": {
                    "timestamp": datetime.now(UTC).isoformat()
                }
            }
        )


async def get_supported_providers_controller(
        registry: OAuthProviderRegistry
) -> SupportedProvidersSchema:
    """
    Controller for getting supported OAuth providers.

    Args:
        registry: OAuth provider registry to get supported providers

    Returns:
        SupportedProvidersSchema with list of supported providers

    Note:
        This controller never raises exceptions - uses fallback if registry fails
    """
    try:
        supported_providers = registry.get_supported_providers()
        return SupportedProvidersSchema(
            providers=supported_providers,
            total_count=len(supported_providers)
        )
    except Exception as e:
        logger.error(f"Error getting supported providers from registry: {str(e)}")
        fallback_providers = ["google"]
        return SupportedProvidersSchema(
            providers=fallback_providers,
            total_count=len(fallback_providers)
        )
