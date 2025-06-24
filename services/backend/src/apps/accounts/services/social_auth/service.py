"""
Google social authentication service.
"""

import logging

from email_validator import validate_email, EmailNotValidError

from oauth.interfaces import OAuthProviderInterface
from oauth.dto import OAuthUserInfo
from oauth.exceptions import OAuthError, TokenVerificationError, UserInfoError

from apps.accounts.services.social_auth.dto import (
    SocialAuthRequest,
    SocialUserProfile,
    SocialAuthResult,
    SocialAuthTokens,
    SocialAuthResponse
)
from apps.accounts.services.social_auth.exceptions import (
    SocialAuthError,
    SocialProviderError,
    SocialTokenError,
    SocialUserInfoError,
    SocialUserValidationError
)
from apps.accounts.services.social_auth.interfaces import SocialAuthServiceInterface

logger = logging.getLogger(__name__)


class GoogleSocialAuthService(SocialAuthServiceInterface):
    """
    Google social authentication service.
    Uses injected OAuth provider for authentication and handles business logic.
    """

    def __init__(self, oauth_provider: OAuthProviderInterface):
        """
        Initialize Google social auth service.
        
        Args:
            oauth_provider: OAuth provider instance (injected)
        """
        self._oauth_provider = oauth_provider
        self.provider_name = oauth_provider.provider_name

    async def authenticate(self, request: SocialAuthRequest) -> SocialAuthResponse:
        """
        Authenticate user through OAuth provider.

        Args:
            request: Social authentication request

        Returns:
            Social authentication response

        Raises:
            SocialAuthError: If authentication fails
        """
        try:
            oauth_user_info = await self._oauth_provider.authenticate_user(request.access_token)

            user_profile = self._convert_to_social_profile(oauth_user_info)

            self._validate_profile(user_profile)

            auth_result = await self._handle_user(user_profile)

            tokens = await self._generate_tokens(auth_result)

            return SocialAuthResponse(
                success=True,
                tokens=tokens,
                user_profile=user_profile,
                is_new_user=not auth_result.user_exists,
                message=f"{self.provider_name.title()} authentication successful",
                provider=self.provider_name
            )

        except TokenVerificationError as e:
            raise SocialTokenError(
                f"Token verification failed: {str(e)}",
                self.provider_name,
                e.status_code,
                e
            )
        except UserInfoError as e:
            raise SocialUserInfoError(
                f"User info extraction failed: {str(e)}",
                self.provider_name,
                e.missing_fields,
                e
            )
        except OAuthError as e:
            raise SocialProviderError(
                f"OAuth error: {str(e)}",
                self.provider_name,
                e
            )
        except SocialAuthError:
            raise
        except Exception as e:
            logger.error(f"Social authentication failed: {str(e)}", exc_info=True)
            raise SocialAuthError(
                f"Authentication failed: {str(e)}",
                self.provider_name,
                e
            )

    async def get_supported_providers(self) -> list[str]:
        """
        Get list of supported providers.

        Returns:
            List with current provider name
        """
        return [self.provider_name]

    def _convert_to_social_profile(self, oauth_info: OAuthUserInfo) -> SocialUserProfile:
        """
        Convert OAuth user info to social profile.

        Args:
            oauth_info: OAuth user information

        Returns:
            Social user profile
        """
        return SocialUserProfile(
            provider=oauth_info.provider,
            provider_id=oauth_info.provider_id,
            email=oauth_info.email,
            name=oauth_info.name,
            first_name=oauth_info.first_name,
            last_name=oauth_info.last_name,
            avatar_url=oauth_info.avatar_url,
            locale=oauth_info.locale,
            verified_email=oauth_info.verified_email
        )

    def _validate_profile(self, profile: SocialUserProfile) -> None:
        """
        Validate social user profile.

        Args:
            profile: Social user profile

        Raises:
            SocialUserValidationError: If profile is invalid
        """
        missing_fields = []

        if not profile.email:
            missing_fields.append("email")
        if not profile.provider_id:
            missing_fields.append("provider_id")
        if not profile.name:
            missing_fields.append("name")

        if missing_fields:
            raise SocialUserValidationError(
                f"Missing required fields: {', '.join(missing_fields)}",
                profile.provider
            )

        try:
            validation_result = validate_email(profile.email)
            normalized_email = validation_result.normalized
            profile.email = normalized_email
        except EmailNotValidError as e:
            raise SocialUserValidationError(
                f"Invalid email format: {str(e)}",
                profile.provider
            )

        if profile.provider == "google" and not profile.verified_email:
                raise SocialUserValidationError(
                    "Google email must be verified",
                    profile.provider
                )

    async def _handle_user(self, profile: SocialUserProfile) -> SocialAuthResult:
        """
        Handle user lookup/creation (placeholder).

        Args:
            profile: Social user profile

        Returns:
            Social authentication result
        """
        # TODO: Real work with the database
        logger.info(f"Handling user for email: {profile.email}")

        return SocialAuthResult(
            success=True,
            user_profile=profile,
            user_exists=False,
            user_id=None,
            message="User handled successfully",
            provider=profile.provider
        )

    async def _generate_tokens(self, auth_result: SocialAuthResult) -> SocialAuthTokens:
        """
        Generate JWT tokens (placeholder).

        Args:
            auth_result: Authentication result

        Returns:
            JWT tokens
        """
        # TODO: Real generation of JWT tokens
        logger.info(f"Generating tokens for user: {auth_result.user_profile.email}")

        return SocialAuthTokens(
            access_token=f"{auth_result.provider}_access_token_123",
            refresh_token=f"{auth_result.provider}_refresh_token_456",
            token_type="bearer",
            expires_in=3600
        )
