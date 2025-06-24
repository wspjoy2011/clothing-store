"""
OAuth dependencies for dependency injection.
"""

from functools import lru_cache

from oauth.factories import OAuthProviderFactory, OAuthProviderRegistry
from oauth.interfaces import OAuthProviderInterface
from oauth.exceptions import ProviderNotSupportedError
from settings.config import config


@lru_cache()
def get_oauth_registry() -> OAuthProviderRegistry:
    """
    Get OAuth provider registry instance (singleton).
    
    Returns:
        OAuth provider registry
    """
    factory = OAuthProviderFactory()
    return OAuthProviderRegistry(factory)


def get_oauth_provider(provider_name: str) -> OAuthProviderInterface:
    """
    Get OAuth provider by name with default configuration.
    
    Args:
        provider_name: Name of the OAuth provider ('google', etc.)
        
    Returns:
        OAuth provider instance
        
    Raises:
        ProviderNotSupportedError: If provider is not supported
        ConfigurationError: If configuration is invalid
    """
    registry = get_oauth_registry()

    provider_configs = {
        "google": config.GOOGLE_OAUTH_CONFIG,
    }

    if provider_name.lower() not in provider_configs:
        raise ProviderNotSupportedError(
            provider_name,
            list(provider_configs.keys())
        )

    provider_config = provider_configs[provider_name.lower()]
    return registry.get_provider(provider_name, provider_config)
