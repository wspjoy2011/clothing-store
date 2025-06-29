"""
Facebook OAuth provider implementation using Authlib.
"""

from typing import Dict, Any

from authlib.integrations.httpx_client import AsyncOAuth2Client
from authlib.common.errors import AuthlibBaseError
import httpx

from oauth.interfaces import OAuthProviderInterface
from oauth.dto import OAuthUserInfo
from oauth.exceptions import TokenVerificationError, UserInfoError, ConfigurationError, OAuthError


class FacebookOAuthProvider(OAuthProviderInterface):
    """
    Facebook OAuth2 provider implementation using Authlib.
    """

    _FACEBOOK_USERINFO_URL = "https://graph.facebook.com/me"
    _FACEBOOK_AUTH_URL = "https://www.facebook.com/v23.0/dialog/oauth"
    _FACEBOOK_TOKEN_URL = "https://graph.facebook.com/v23.0/oauth/access_token"

    def __init__(self, client_id: str, client_secret: str):
        """
        Initialize Facebook OAuth provider.

        Args:
            client_id: Facebook App ID
            client_secret: Facebook App Secret
        """
        self._client_id = client_id
        self._client_secret = client_secret
        self.validate_config()

        self._oauth_client = AsyncOAuth2Client(
            client_id=self._client_id,
            client_secret=self._client_secret
        )

    @property
    def provider_name(self) -> str:
        """Return provider name."""
        return "facebook"

    async def verify_token(self, access_token: str) -> Dict[str, Any]:
        """
        Verify Facebook access token and get user info.

        Args:
            access_token: Facebook access token

        Returns:
            User data from Facebook

        Raises:
            TokenVerificationError: If token verification fails
        """
        if not access_token:
            raise TokenVerificationError(
                self.provider_name,
                "Access token is required"
            )

        try:
            self._oauth_client.token = {"access_token": access_token}

            params = {
                "fields": "id,name,email,first_name,last_name,picture,locale,verified"
            }

            response = await self._oauth_client.get(
                self._FACEBOOK_USERINFO_URL,
                params=params
            )

            if response.status_code != 200:
                raise TokenVerificationError(
                    self.provider_name,
                    f"Failed to get user info: {response.text}",
                    response.status_code
                )

            user_data = response.json()

            if "error" in user_data:
                error_msg = user_data["error"].get("message", "Unknown Facebook API error")
                raise TokenVerificationError(
                    self.provider_name,
                    f"Facebook API error: {error_msg}"
                )

            return user_data

        except AuthlibBaseError as e:
            raise TokenVerificationError(
                self.provider_name,
                f"Authlib error during token verification: {str(e)}"
            )
        except httpx.HTTPError as e:
            raise TokenVerificationError(
                self.provider_name,
                f"Network error during token verification: {str(e)}"
            )
        except Exception as e:
            if isinstance(e, TokenVerificationError):
                raise
            raise TokenVerificationError(
                self.provider_name,
                f"Unexpected error during token verification: {str(e)}"
            )

    def extract_user_info(self, raw_data: Dict[str, Any]) -> OAuthUserInfo:
        """
        Extract user information from Facebook's response.

        Args:
            raw_data: Raw user data from Facebook

        Returns:
            Standardized user information

        Raises:
            UserInfoError: If required fields are missing
        """
        try:
            email = raw_data.get("email")
            facebook_id = raw_data.get("id")
            name = raw_data.get("name")

            missing_fields = []
            if not email:
                missing_fields.append("email")
            if not facebook_id:
                missing_fields.append("id")
            if not name:
                missing_fields.append("name")

            if missing_fields:
                raise UserInfoError(
                    self.provider_name,
                    f"Missing required fields: {', '.join(missing_fields)}",
                    missing_fields
                )

            first_name = raw_data.get("first_name")
            last_name = raw_data.get("last_name")

            avatar_url = None
            picture_data = raw_data.get("picture")
            if picture_data and isinstance(picture_data, dict):
                data = picture_data.get("data", {})
                if not data.get("is_silhouette", True):  # Only use real pictures
                    avatar_url = data.get("url")

            locale = raw_data.get("locale")
            verified_email = raw_data.get("verified", True)

            if isinstance(verified_email, str):
                verified_email = verified_email.lower() in ("true", "1", "yes")

            return OAuthUserInfo(
                provider=self.provider_name,
                provider_id=str(facebook_id),
                email=email,
                name=name,
                first_name=first_name,
                last_name=last_name,
                avatar_url=avatar_url,
                locale=locale,
                verified_email=bool(verified_email),
                raw_data=raw_data
            )

        except Exception as e:
            if isinstance(e, UserInfoError):
                raise
            raise UserInfoError(
                self.provider_name,
                f"Failed to extract user info: {str(e)}"
            )

    async def authenticate_user(self, access_token: str) -> OAuthUserInfo:
        """
        Complete Facebook authentication flow.

        Args:
            access_token: Facebook access token

        Returns:
            Standardized user information

        Raises:
            OAuthError: If authentication fails
        """
        try:
            raw_data = await self.verify_token(access_token)
            user_info = self.extract_user_info(raw_data)
            return user_info

        except Exception as e:
            raise OAuthError(
                f"Facebook authentication failed: {str(e)}"
            ) from e

    def get_required_scopes(self) -> list[str]:
        """
        Return required OAuth scopes for Facebook.

        Returns:
            List of required scopes
        """
        return [
            "email",
            "public_profile"
        ]

    def validate_config(self) -> bool:
        """
        Validate Facebook OAuth configuration.

        Returns:
            True if configuration is valid

        Raises:
            ConfigurationError: If configuration is invalid
        """
        if not self._client_id:
            raise ConfigurationError(
                self.provider_name,
                "client_id is required"
            )

        if not self._client_secret:
            raise ConfigurationError(
                self.provider_name,
                "client_secret is required"
            )

        if not self._client_id.isdigit():
            raise ConfigurationError(
                self.provider_name,
                "client_id should be a numeric Facebook App ID"
            )

        return True

    def get_authorization_url(self, redirect_uri: str, state: str = None) -> str:
        """
        Generate Facebook OAuth2 authorization URL using Authlib.

        Args:
            redirect_uri: Redirect URI after authorization
            state: Optional state parameter for security

        Returns:
            Authorization URL
        """
        authorization_url, _ = self._oauth_client.create_authorization_url(
            self._FACEBOOK_AUTH_URL,
            redirect_uri=redirect_uri,
            scope=" ".join(self.get_required_scopes()),
            state=state,
            response_type="code"
        )

        return authorization_url

    async def exchange_code_for_token(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token using Authlib.

        Args:
            code: Authorization code from Facebook
            redirect_uri: Redirect URI used in authorization

        Returns:
            Token response from Facebook

        Raises:
            TokenVerificationError: If code exchange fails
        """
        try:
            token = await self._oauth_client.fetch_token(
                self._FACEBOOK_TOKEN_URL,
                code=code,
                redirect_uri=redirect_uri
            )
            return token

        except AuthlibBaseError as e:
            raise TokenVerificationError(
                self.provider_name,
                f"Failed to exchange code for token: {str(e)}"
            )
        except Exception as e:
            raise TokenVerificationError(
                self.provider_name,
                f"Unexpected error during code exchange: {str(e)}"
            )
