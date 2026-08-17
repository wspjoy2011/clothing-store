"""
Dependencies for social authentication service.
"""

from typing import Callable

from fastapi import Depends

from oauth.dependencies import get_oauth_registry
from oauth.factories import OAuthProviderRegistry
from oauth.exceptions import ProviderNotSupportedError
from settings.config import config
from apps.accounts.services.social_auth.service import SocialAuthService
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
from db.dependencies import get_transaction_manager
from db.interfaces import TransactionManagerInterface


def get_social_auth_service_resolver(
        registry: OAuthProviderRegistry = Depends(get_oauth_registry),
        user_repository: UserRepositoryInterface = Depends(get_user_repository),
        user_group_repository: UserGroupRepositoryInterface = Depends(get_user_group_repository),
        token_repository: TokenRepositoryInterface = Depends(get_token_repository),
        password_manager: PasswordManagerInterface = Depends(get_password_manager),
        jwt_manager: JWTManagerInterface = Depends(get_jwt_manager),
        email_sender: EmailSenderInterface = Depends(get_email_sender_dependency),
        transaction_manager: TransactionManagerInterface = Depends(get_transaction_manager)
) -> Callable[[str], SocialAuthServiceInterface]:
    """
    Get a resolver building the social auth service of one named provider

    The service is built when the provider is known, not while the request is being
    wired: resolving every provider up front means a credential missing for one of
    them breaks sign-in through all the others.

    Args:
        registry: OAuth provider registry
        user_repository: Repository for user data operations
        user_group_repository: Repository for user group operations
        token_repository: Repository for token operations
        password_manager: Manager for password hashing and verification
        jwt_manager: Manager for JWT token operations
        email_sender: Email sender for notifications
        transaction_manager: Manager owning transaction boundaries

    Returns:
        Callable taking a provider name and returning its service

    Raises:
        ProviderNotSupportedError: Raised by the resolver for an unknown provider
    """
    def resolve(provider_name: str) -> SocialAuthServiceInterface:
        """
        Build the service of one provider

        Args:
            provider_name: Provider the caller asked for

        Returns:
            Social auth service bound to that provider

        Raises:
            ProviderNotSupportedError: If the provider is unknown
        """
        return get_social_auth_service(
            provider_name=provider_name,
            registry=registry,
            user_repository=user_repository,
            user_group_repository=user_group_repository,
            token_repository=token_repository,
            password_manager=password_manager,
            jwt_manager=jwt_manager,
            email_sender=email_sender,
            transaction_manager=transaction_manager
        )

    return resolve


def get_google_social_auth_service(
        registry: OAuthProviderRegistry = Depends(get_oauth_registry),
        user_repository: UserRepositoryInterface = Depends(get_user_repository),
        user_group_repository: UserGroupRepositoryInterface = Depends(get_user_group_repository),
        token_repository: TokenRepositoryInterface = Depends(get_token_repository),
        password_manager: PasswordManagerInterface = Depends(get_password_manager),
        jwt_manager: JWTManagerInterface = Depends(get_jwt_manager),
        email_sender: EmailSenderInterface = Depends(get_email_sender_dependency),
        transaction_manager: TransactionManagerInterface = Depends(get_transaction_manager)
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
        transaction_manager: Manager owning transaction boundaries

    Returns:
        Google social auth service instance
    """
    provider_config = config.GOOGLE_OAUTH_CONFIG
    oauth_provider = registry.get_provider("google", provider_config)

    return SocialAuthService(
        oauth_provider=oauth_provider,
        user_repository=user_repository,
        user_group_repository=user_group_repository,
        token_repository=token_repository,
        password_manager=password_manager,
        jwt_manager=jwt_manager,
        email_sender=email_sender,
        transaction_manager=transaction_manager
    )


def get_facebook_social_auth_service(
        registry: OAuthProviderRegistry = Depends(get_oauth_registry),
        user_repository: UserRepositoryInterface = Depends(get_user_repository),
        user_group_repository: UserGroupRepositoryInterface = Depends(get_user_group_repository),
        token_repository: TokenRepositoryInterface = Depends(get_token_repository),
        password_manager: PasswordManagerInterface = Depends(get_password_manager),
        jwt_manager: JWTManagerInterface = Depends(get_jwt_manager),
        email_sender: EmailSenderInterface = Depends(get_email_sender_dependency),
        transaction_manager: TransactionManagerInterface = Depends(get_transaction_manager)
) -> SocialAuthServiceInterface:
    """
    Get Facebook social authentication service.

    Args:
        registry: OAuth provider registry
        user_repository: Repository for user data operations
        user_group_repository: Repository for user group operations
        token_repository: Repository for token operations
        password_manager: Manager for password hashing and verification
        jwt_manager: Manager for JWT token operations
        email_sender: Email sender for notifications
        transaction_manager: Manager owning transaction boundaries

    Returns:
        Facebook social auth service instance
    """
    provider_config = config.FACEBOOK_OAUTH_CONFIG
    oauth_provider = registry.get_provider("facebook", provider_config)

    return SocialAuthService(
        oauth_provider=oauth_provider,
        user_repository=user_repository,
        user_group_repository=user_group_repository,
        token_repository=token_repository,
        password_manager=password_manager,
        jwt_manager=jwt_manager,
        email_sender=email_sender,
        transaction_manager=transaction_manager
    )


def get_social_auth_service(
        provider_name: str,
        registry: OAuthProviderRegistry,
        user_repository: UserRepositoryInterface,
        user_group_repository: UserGroupRepositoryInterface,
        token_repository: TokenRepositoryInterface,
        password_manager: PasswordManagerInterface,
        jwt_manager: JWTManagerInterface,
        email_sender: EmailSenderInterface,
        transaction_manager: TransactionManagerInterface
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
        transaction_manager: Manager owning transaction boundaries

    Returns:
        Social auth service instance

    Raises:
        ProviderNotSupportedError: If provider is not supported
        ValueError: If provider configuration is missing
    """
    provider_configs = {
        "google": config.GOOGLE_OAUTH_CONFIG,
        "facebook": config.FACEBOOK_OAUTH_CONFIG,
    }

    if provider_name.lower() not in provider_configs:
        raise ProviderNotSupportedError(
            provider_name,
            list(provider_configs.keys())
        )

    provider_config = provider_configs[provider_name.lower()]
    oauth_provider = registry.get_provider(provider_name, provider_config)

    return SocialAuthService(
        oauth_provider=oauth_provider,
        user_repository=user_repository,
        user_group_repository=user_group_repository,
        token_repository=token_repository,
        password_manager=password_manager,
        jwt_manager=jwt_manager,
        email_sender=email_sender,
        transaction_manager=transaction_manager
    )
