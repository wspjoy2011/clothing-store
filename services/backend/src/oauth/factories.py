"""
OAuth provider factory implementation.
"""

from typing import Dict, Any, Callable

from oauth.interfaces import OAuthProviderInterface, OAuthProviderFactoryInterface
from oauth.exceptions import ProviderNotSupportedError, ConfigurationError
from oauth.providers.google import GoogleOAuthProvider
from oauth.providers.facebook import FacebookOAuthProvider


class OAuthProviderFactory(OAuthProviderFactoryInterface):
    """
    Factory for creating OAuth provider instances using strategy pattern.
    """

    def __init__(self):
        """Initialize factory with provider strategies."""
        self._providers: Dict[str, Callable[[Dict[str, Any]], OAuthProviderInterface]] = {
            "google": self._create_google_provider,
            "facebook": self._create_facebook_provider,
        }

    def create_provider(self, provider_name: str, config: Dict[str, Any]) -> OAuthProviderInterface:
        """
        Create an OAuth provider instance using strategy pattern.

        Args:
            provider_name: Name of the provider to create
            config: Configuration dictionary for the provider

        Returns:
            OAuth provider instance

        Raises:
            ProviderNotSupportedError: If provider is not supported
            ConfigurationError: If configuration is invalid
        """
        if not self.is_provider_supported(provider_name):
            raise ProviderNotSupportedError(
                provider_name,
                self.get_supported_providers()
            )

        try:
            provider_strategy = self._providers[provider_name]
            return provider_strategy(config)
        except Exception as e:
            if isinstance(e, (ProviderNotSupportedError, ConfigurationError)):
                raise
            raise ConfigurationError(
                provider_name,
                f"Failed to create provider: {str(e)}"
            )

    def get_supported_providers(self) -> list[str]:
        """
        Get list of supported provider names.

        Returns:
            List of supported provider names
        """
        return list(self._providers.keys())

    def is_provider_supported(self, provider_name: str) -> bool:
        """
        Check if a provider is supported.

        Args:
            provider_name: Name of the provider to check

        Returns:
            True if provider is supported, False otherwise
        """
        return provider_name.lower() in self._providers

    def register_provider(
            self,
            provider_name: str,
            provider_strategy: Callable[[Dict[str, Any]], OAuthProviderInterface]
    ) -> None:
        """
        Register a new provider strategy.

        Args:
            provider_name: Name of the provider
            provider_strategy: Function that creates provider instance
        """
        self._providers[provider_name.lower()] = provider_strategy

    def _create_google_provider(self, config: Dict[str, Any]) -> GoogleOAuthProvider:
        """
        Create Google OAuth provider instance.

        Args:
            config: Google OAuth configuration

        Returns:
            GoogleOAuthProvider instance

        Raises:
            ConfigurationError: If required config keys are missing
        """
        required_keys = ["client_id", "client_secret"]
        missing_keys = [key for key in required_keys if key not in config]

        if missing_keys:
            raise ConfigurationError(
                "google",
                f"Missing required configuration keys: {', '.join(missing_keys)}"
            )

        return GoogleOAuthProvider(
            client_id=config["client_id"],
            client_secret=config["client_secret"]
        )

    def _create_facebook_provider(self, config: Dict[str, Any]) -> FacebookOAuthProvider:
        """
        Create Facebook OAuth provider instance.

        Args:
            config: Facebook OAuth configuration

        Returns:
            FacebookOAuthProvider instance

        Raises:
            ConfigurationError: If required config keys are missing
        """
        required_keys = ["client_id", "client_secret"]
        missing_keys = [key for key in required_keys if key not in config]

        if missing_keys:
            raise ConfigurationError(
                "facebook",
                f"Missing required configuration keys: {', '.join(missing_keys)}"
            )

        return FacebookOAuthProvider(
            client_id=config["client_id"],
            client_secret=config["client_secret"]
        )


class OAuthProviderRegistry:
    """
    Registry for managing OAuth providers with caching.
    """

    def __init__(self, factory: OAuthProviderFactoryInterface):
        """
        Initialize registry with factory.

        Args:
            factory: OAuth provider factory
        """
        self._factory = factory
        self._providers_cache: Dict[str, OAuthProviderInterface] = {}

    def get_provider(self, provider_name: str, config: Dict[str, Any]) -> OAuthProviderInterface:
        """
        Get OAuth provider instance with caching.

        Args:
            provider_name: Name of the provider
            config: Configuration for the provider

        Returns:
            OAuth provider instance
        """
        cache_key = f"{provider_name}_{hash(frozenset(config.items()))}"

        if cache_key not in self._providers_cache:
            self._providers_cache[cache_key] = self._factory.create_provider(
                provider_name,
                config
            )

        return self._providers_cache[cache_key]

    def clear_cache(self) -> None:
        """Clear providers cache."""
        self._providers_cache.clear()

    def get_supported_providers(self) -> list[str]:
        """Get list of supported providers."""
        return self._factory.get_supported_providers()

    def is_provider_supported(self, provider_name: str) -> bool:
        """Check if provider is supported."""
        return self._factory.is_provider_supported(provider_name)
