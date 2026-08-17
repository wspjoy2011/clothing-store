"""Google OAuth provider implementation."""

from typing import Dict, Any
import httpx

from oauth.interfaces import OAuthProviderInterface
from oauth.dto import OAuthUserInfo
from oauth.exceptions import TokenVerificationError, UserInfoError, ConfigurationError, OAuthError


class GoogleOAuthProvider(OAuthProviderInterface):
    """Google OAuth2 provider implementation

    Every verification uses its own HTTP client: a client shared by the process
    would carry one request's credentials into another.
    """

    _GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
    _GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    _GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
    _GOOGLE_TOKENINFO_URL = "https://oauth2.googleapis.com/tokeninfo"
    _REQUEST_TIMEOUT = 10.0

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

    @property
    def provider_name(self) -> str:
        """Return provider name."""
        return "google"

    async def verify_token(self, access_token: str) -> Dict[str, Any]:
        """
        Verify that the token was issued to this application, then read the profile

        The audience check is what makes the token ours: Google's userinfo endpoint
        answers for any valid token, including one issued to somebody else's client,
        so a token accepted without checking its audience lets the holder of any
        Google token sign in as its owner.

        Args:
            access_token: Google access token

        Returns:
            User data from Google

        Raises:
            TokenVerificationError: If the token is rejected, belongs to another
                application, or the profile cannot be read
        """
        if not access_token:
            raise TokenVerificationError(
                self.provider_name,
                "Access token is required"
            )

        try:
            async with httpx.AsyncClient(timeout=self._REQUEST_TIMEOUT) as client:
                token_info = await self._read_token_info(client, access_token)
                self._require_own_audience(token_info)
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

    async def _read_token_info(self, client: httpx.AsyncClient, access_token: str) -> Dict[str, Any]:
        """
        Ask Google what the token is and who it was issued to

        Args:
            client: HTTP client used for this verification
            access_token: Token presented by the caller

        Returns:
            Token metadata as reported by Google

        Raises:
            TokenVerificationError: If Google does not recognise the token
        """
        response = await client.get(
            self._GOOGLE_TOKENINFO_URL,
            params={"access_token": access_token}
        )

        if response.status_code != 200:
            raise TokenVerificationError(
                self.provider_name,
                "Token was rejected by Google"
            )

        return response.json()

    def _require_own_audience(self, token_info: Dict[str, Any]) -> None:
        """
        Refuse a token that was issued to a different OAuth client

        Args:
            token_info: Token metadata as reported by Google

        Raises:
            TokenVerificationError: If the audience is not this application
        """
        if token_info.get("aud") != self._client_id:
            raise TokenVerificationError(
                self.provider_name,
                "Token was issued to another application"
            )

    async def _read_user_info(self, client: httpx.AsyncClient, access_token: str) -> Dict[str, Any]:
        """
        Read the profile of the token owner

        Args:
            client: HTTP client used for this verification
            access_token: Token already confirmed to be ours

        Returns:
            Raw profile data from Google

        Raises:
            TokenVerificationError: If the profile cannot be read
        """
        response = await client.get(
            self._GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"}
        )

        if response.status_code != 200:
            raise TokenVerificationError(
                self.provider_name,
                "Profile could not be read from Google",
                response.status_code
            )

        return response.json()

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
            verified_email = raw_data.get("verified_email", False)

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


