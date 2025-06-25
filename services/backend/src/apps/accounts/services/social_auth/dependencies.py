"""
Dependencies for social authentication service.
"""

from fastapi import Depends

from oauth.dependencies import get_oauth_registry
from oauth.factories import OAuthProviderRegistry
from oauth.exceptions import ProviderNotSupportedError
from settings.config import config
from apps.accounts.services.social_auth.service import GoogleSocialAuthService
from apps.accounts.services.social_auth.interfaces import SocialAuthServiceInterface


def get_google_social_auth_service(
        registry: OAuthProviderRegistry = Depends(get_oauth_registry)
) -> SocialAuthServiceInterface:
    """
    Get Google social authentication service.

    Args:
        registry: OAuth provider registry

    Returns:
        Google social auth service instance
    """
    provider_config = config.GOOGLE_OAUTH_CONFIG
    oauth_provider = registry.get_provider("google", provider_config)
    return GoogleSocialAuthService(oauth_provider)


def get_social_auth_service(
        provider_name: str,
        registry: OAuthProviderRegistry
) -> SocialAuthServiceInterface:
    """
    Get social authentication service by provider name.
    NOTE: This function is NOT for FastAPI Depends - use specific provider functions instead.

    Args:
        provider_name: Name of the OAuth provider
        registry: OAuth provider registry

    Returns:
        Social auth service instance

    Raises:
        ProviderNotSupportedError: If provider is not supported
        ValueError: If provider configuration is missing
    """
    provider_configs = {
        "google": config.GOOGLE_OAUTH_CONFIG,
    }

    if provider_name.lower() not in provider_configs:
        raise ProviderNotSupportedError(
            provider_name,
            list(provider_configs.keys())
        )

    provider_config = provider_configs[provider_name.lower()]
    oauth_provider = registry.get_provider(provider_name, provider_config)

    if provider_name.lower() == "google":
        return GoogleSocialAuthService(oauth_provider)

    raise ValueError(f"Unsupported social provider: {provider_name}")
