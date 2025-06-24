"""
OAuth provider interfaces.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any

from oauth.dto import OAuthUserInfo


class OAuthProviderInterface(ABC):
    """
    Interface for OAuth authentication providers.

    All OAuth providers must implement this interface to ensure
    consistent behavior across different social login services.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """
        Return the name of the OAuth provider.

        Returns:
            Provider name (e.g., 'google', 'facebook')
        """
        pass

    @abstractmethod
    async def verify_token(self, access_token: str) -> Dict[str, Any]:
        """
        Verify the access token with the OAuth provider.

        Args:
            access_token: Access token received from the frontend

        Returns:
            Raw user data from the provider

        Raises:
            TokenVerificationError: If token verification fails
        """
        pass

    @abstractmethod
    def extract_user_info(self, raw_data: Dict[str, Any]) -> OAuthUserInfo:
        """
        Extract standardized user information from provider's raw data.

        Args:
            raw_data: Raw user data returned by verify_token()

        Returns:
            Standardized user information

        Raises:
            UserInfoError: If required user data is missing or invalid
        """
        pass

    @abstractmethod
    async def authenticate_user(self, access_token: str) -> OAuthUserInfo:
        """
        Complete authentication flow: verify token and extract user info.

        Args:
            access_token: Access token received from the frontend

        Returns:
            Standardized user information

        Raises:
            OAuthError: If authentication fails at any step
        """
        pass

    @abstractmethod
    def get_required_scopes(self) -> list[str]:
        """
        Return the list of OAuth scopes required by this provider.

        Returns:
            List of required OAuth scopes
        """
        pass

    @abstractmethod
    def validate_config(self) -> bool:
        """
        Validate provider configuration.

        Returns:
            True if configuration is valid

        Raises:
            ConfigurationError: If configuration is invalid
        """
        pass


class OAuthProviderFactoryInterface(ABC):
    """
    Interface for OAuth provider factory.
    """

    @abstractmethod
    def create_provider(self, provider_name: str, config: Dict[str, Any]) -> OAuthProviderInterface:
        """
        Create an OAuth provider instance.

        Args:
            provider_name: Name of the provider to create
            config: Configuration dictionary for the provider

        Returns:
            OAuth provider instance

        Raises:
            ProviderNotSupportedError: If provider is not supported
            ConfigurationError: If configuration is invalid
        """
        pass

    @abstractmethod
    def get_supported_providers(self) -> list[str]:
        """
        Get list of supported provider names.

        Returns:
            List of supported provider names
        """
        pass

    @abstractmethod
    def is_provider_supported(self, provider_name: str) -> bool:
        """
        Check if a provider is supported.

        Args:
            provider_name: Name of the provider to check

        Returns:
            True if provider is supported, False otherwise
        """
        pass
