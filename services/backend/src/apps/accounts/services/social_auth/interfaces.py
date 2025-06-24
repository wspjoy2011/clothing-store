"""
Interface for social authentication service.
"""

from abc import ABC, abstractmethod

from apps.accounts.services.social_auth.dto import SocialAuthRequest, SocialAuthResponse


class SocialAuthServiceInterface(ABC):
    """
    Interface for social authentication service.
    """

    @abstractmethod
    async def authenticate(self, request: SocialAuthRequest) -> SocialAuthResponse:
        """
        Authenticate user through social provider.

        Args:
            request: Social authentication request

        Returns:
            Social authentication response
        """
        pass

    @abstractmethod
    async def get_supported_providers(self) -> list[str]:
        """
        Get list of supported providers.

        Returns:
            List of supported provider names
        """
        pass
