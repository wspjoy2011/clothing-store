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
from apps.accounts.interfaces.repositories import (
    UserRepositoryInterface,
    UserGroupRepositoryInterface,
    TokenRepositoryInterface
)
from apps.accounts.dependencies import (
    get_user_repository,
    get_user_group_repository,
    get_token_repository
)
from security.dependencies import get_password_manager, get_jwt_manager
from security.interfaces import PasswordManagerInterface, JWTManagerInterface
from notifications.dependencies import get_email_sender_dependency
from notifications.email.interfaces import EmailSenderInterface


def get_google_social_auth_service(
        registry: OAuthProviderRegistry = Depends(get_oauth_registry),
        user_repository: UserRepositoryInterface = Depends(get_user_repository),
        user_group_repository: UserGroupRepositoryInterface = Depends(get_user_group_repository),
        token_repository: TokenRepositoryInterface = Depends(get_token_repository),
        password_manager: PasswordManagerInterface = Depends(get_password_manager),
        jwt_manager: JWTManagerInterface = Depends(get_jwt_manager),
        email_sender: EmailSenderInterface = Depends(get_email_sender_dependency)
) -> SocialAuthServiceInterface:
    """
    Get Google social authentication service.

    Args:
        registry: OAuth provider registry
        user_repository: Repository for user data operations
        user_group_repository: Repository for user group operations
        token_repository: Repository for token operations
        password_manager: Manager for password hashing and verification
        jwt_manager: Manager for JWT token operations
        email_sender: Email sender for notifications

    Returns:
        Google social auth service instance
    """
    provider_config = config.GOOGLE_OAUTH_CONFIG
    oauth_provider = registry.get_provider("google", provider_config)

    return GoogleSocialAuthService(
        oauth_provider=oauth_provider,
        user_repository=user_repository,
        user_group_repository=user_group_repository,
        token_repository=token_repository,
        password_manager=password_manager,
        jwt_manager=jwt_manager,
        email_sender=email_sender
    )


def get_social_auth_service(
        provider_name: str,
        registry: OAuthProviderRegistry,
        user_repository: UserRepositoryInterface,
        user_group_repository: UserGroupRepositoryInterface,
        token_repository: TokenRepositoryInterface,
        password_manager: PasswordManagerInterface,
        jwt_manager: JWTManagerInterface,
        email_sender: EmailSenderInterface
) -> SocialAuthServiceInterface:
    """
    Get social authentication service by provider name.
    NOTE: This function is NOT for FastAPI Depends - use specific provider functions instead.

    Args:
        provider_name: Name of the OAuth provider
        registry: OAuth provider registry
        user_repository: Repository for user data operations
        user_group_repository: Repository for user group operations
        token_repository: Repository for token operations
        password_manager: Manager for password hashing and verification
        jwt_manager: Manager for JWT token operations
        email_sender: Email sender for notifications

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
        return GoogleSocialAuthService(
            oauth_provider=oauth_provider,
            user_repository=user_repository,
            user_group_repository=user_group_repository,
            token_repository=token_repository,
            password_manager=password_manager,
            jwt_manager=jwt_manager,
            email_sender=email_sender
        )

    raise ValueError(f"Unsupported social provider: {provider_name}")
