"""
Google OAuth provider implementation using Authlib.
"""

from typing import Dict, Any
from authlib.integrations.httpx_client import AsyncOAuth2Client
from authlib.common.errors import AuthlibBaseError
import httpx

from oauth.interfaces import OAuthProviderInterface
from oauth.dto import OAuthUserInfo
from oauth.exceptions import TokenVerificationError, UserInfoError, ConfigurationError, OAuthError


class GoogleOAuthProvider(OAuthProviderInterface):
    """
    Google OAuth2 provider implementation using Authlib.
    """

    _GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
    _GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    _GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"

    def __init__(self, client_id: str, client_secret: str):
        """
        Initialize Google OAuth provider.

        Args:
            client_id: Google OAuth2 client ID
            client_secret: Google OAuth2 client secret
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
        return "google"

    async def verify_token(self, access_token: str) -> Dict[str, Any]:
        """
        Verify Google access token using Authlib and get user info.

        Args:
            access_token: Google access token

        Returns:
            User data from Google

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

            response = await self._oauth_client.get(self._GOOGLE_USERINFO_URL)

            if response.status_code != 200:
                raise TokenVerificationError(
                    self.provider_name,
                    f"Failed to get user info: {response.text}",
                    response.status_code
                )

            user_data = response.json()
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
        Extract user information from Google's response.

        Args:
            raw_data: Raw user data from Google

        Returns:
            Standardized user information

        Raises:
            UserInfoError: If required fields are missing
        """
        try:
            email = raw_data.get("email")
            google_id = raw_data.get("id")
            name = raw_data.get("name")

            missing_fields = []
            if not email:
                missing_fields.append("email")
            if not google_id:
                missing_fields.append("id")
            if not name:
                missing_fields.append("name")

            if missing_fields:
                raise UserInfoError(
                    self.provider_name,
                    f"Missing required fields: {', '.join(missing_fields)}",
                    missing_fields
                )

            first_name = raw_data.get("given_name")
            last_name = raw_data.get("family_name")
            avatar_url = raw_data.get("picture")
            locale = raw_data.get("locale")
            verified_email = raw_data.get("verified_email", True)

            if isinstance(verified_email, str):
                verified_email = verified_email.lower() in ("true", "1", "yes")

            return OAuthUserInfo(
                provider=self.provider_name,
                provider_id=str(google_id),
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
        Complete Google authentication flow.

        Args:
            access_token: Google access token

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
                f"Google authentication failed: {str(e)}"
            ) from e

    def get_required_scopes(self) -> list[str]:
        """
        Return required OAuth scopes for Google.

        Returns:
            List of required scopes
        """
        return [
            "openid",
            "email",
            "profile"
        ]

    def validate_config(self) -> bool:
        """
        Validate Google OAuth configuration.

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

        if not self._client_id.endswith(".apps.googleusercontent.com"):
            raise ConfigurationError(
                self.provider_name,
                "client_id should end with .apps.googleusercontent.com"
            )

        return True

    def get_authorization_url(self, redirect_uri: str, state: str = None) -> str:
        """
        Generate Google OAuth2 authorization URL using Authlib.

        Args:
            redirect_uri: Redirect URI after authorization
            state: Optional state parameter for security

        Returns:
            Authorization URL
        """
        authorization_url, _ = self._oauth_client.create_authorization_url(
            self._GOOGLE_AUTH_URL,
            redirect_uri=redirect_uri,
            scope=" ".join(self.get_required_scopes()),
            state=state,
            access_type="offline",
            include_granted_scopes="true"
        )

        return authorization_url

    async def exchange_code_for_token(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token using Authlib.

        Args:
            code: Authorization code from Google
            redirect_uri: Redirect URI used in authorization

        Returns:
            Token response from Google

        Raises:
            TokenVerificationError: If code exchange fails
        """
        try:
            token = await self._oauth_client.fetch_token(
                self._GOOGLE_TOKEN_URL,
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
