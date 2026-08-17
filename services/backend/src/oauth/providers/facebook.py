"""Facebook OAuth provider implementation."""

from typing import Any, Dict

import httpx

from oauth.dto import OAuthUserInfo
from oauth.exceptions import ConfigurationError, OAuthError, TokenVerificationError, UserInfoError
from oauth.interfaces import OAuthProviderInterface


class FacebookOAuthProvider(OAuthProviderInterface):
    """Facebook OAuth2 provider implementation

    Every verification uses its own HTTP client: a client shared by the process
    would carry one request's credentials into another.
    """

    _FACEBOOK_USERINFO_URL = "https://graph.facebook.com/me"
    _FACEBOOK_DEBUG_TOKEN_URL = "https://graph.facebook.com/debug_token"
    _REQUEST_TIMEOUT = 10.0
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

    @property
    def provider_name(self) -> str:
        """Return provider name."""
        return "facebook"

    async def verify_token(self, access_token: str) -> Dict[str, Any]:
        """
        Verify that the token belongs to this app, then read the profile

        The app check is what makes the token ours: the graph API answers for any
        valid token, including one issued to somebody else's app, so a token
        accepted without checking its app lets the holder of any Facebook token
        sign in as its owner.

        Args:
            access_token: Facebook access token

        Returns:
            User data from Facebook

        Raises:
            TokenVerificationError: If the token is rejected, belongs to another
                app, or the profile cannot be read
        """
        if not access_token:
            raise TokenVerificationError(
                self.provider_name,
                "Access token is required"
            )

        try:
            async with httpx.AsyncClient(timeout=self._REQUEST_TIMEOUT) as client:
                token_debug = await self._read_token_debug(client, access_token)
                self._require_own_app(token_debug)
                return await self._read_user_info(client, access_token)

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

    async def _read_token_debug(self, client: httpx.AsyncClient, access_token: str) -> Dict[str, Any]:
        """
        Ask Facebook what the token is and which app it was issued to

        Args:
            client: HTTP client used for this verification
            access_token: Token presented by the caller

        Returns:
            Token metadata as reported by Facebook

        Raises:
            TokenVerificationError: If Facebook does not recognise the token
        """
        response = await client.get(
            self._FACEBOOK_DEBUG_TOKEN_URL,
            params={
                "input_token": access_token,
                "access_token": f"{self._client_id}|{self._client_secret}"
            }
        )

        if response.status_code != 200:
            raise TokenVerificationError(
                self.provider_name,
                "Token was rejected by Facebook"
            )

        return response.json().get("data", {})

    def _require_own_app(self, token_debug: Dict[str, Any]) -> None:
        """
        Refuse a token that is invalid or was issued to a different app

        Args:
            token_debug: Token metadata as reported by Facebook

        Raises:
            TokenVerificationError: If the token is not valid for this app
        """
        if not token_debug.get("is_valid"):
            raise TokenVerificationError(
                self.provider_name,
                "Token is not valid"
            )

        if str(token_debug.get("app_id")) != str(self._client_id):
            raise TokenVerificationError(
                self.provider_name,
                "Token was issued to another application"
            )

    async def _read_user_info(self, client: httpx.AsyncClient, access_token: str) -> Dict[str, Any]:
        """
        Read the profile of the token owner

        Args:
            client: HTTP client used for this verification
            access_token: Token already confirmed to belong to this app

        Returns:
            Raw profile data from Facebook

        Raises:
            TokenVerificationError: If the profile cannot be read
        """
        response = await client.get(
            self._FACEBOOK_USERINFO_URL,
            params={"fields": "id,name,email,first_name,last_name,picture,locale,verified"},
            headers={"Authorization": f"Bearer {access_token}"}
        )

        if response.status_code != 200:
            raise TokenVerificationError(
                self.provider_name,
                "Profile could not be read from Facebook",
                response.status_code
            )

        return response.json()

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
            verified_email = raw_data.get("verified", False)

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


