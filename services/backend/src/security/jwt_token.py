from jose import jwt
from jose.exceptions import JWTError, JWTClaimsError, ExpiredSignatureError, JWSSignatureError
from datetime import datetime, timedelta, timezone
from typing import Dict, Any

from security.interfaces import JWTManagerInterface
from security.exceptions import (
    TokenCreationError,
    TokenVerificationError,
    InvalidTokenError,
    ExpiredTokenError,
    TokenSignatureError,
    InvalidTokenTypeError,
    EmptyTokenError
)


class JWTManager(JWTManagerInterface):
    """JWT token manager implementation."""

    def __init__(
            self,
            access_secret: str,
            refresh_secret: str,
            algorithm: str,
            access_expire_minutes: int,
            refresh_expire_minutes: int
    ):
        """
        Initialize JWT manager with configuration.

        Args:
            access_secret: Secret key for access tokens
            refresh_secret: Secret key for refresh tokens
            algorithm: JWT signing algorithm
            access_expire_minutes: Access token expiration time in minutes
            refresh_expire_minutes: Refresh token expiration time in minutes
        """
        self._access_secret = access_secret
        self._refresh_secret = refresh_secret
        self._algorithm = algorithm
        self._access_expire_minutes = access_expire_minutes
        self._refresh_expire_minutes = refresh_expire_minutes

    def create_access_token(self, data: Dict[str, Any]) -> str:
        """
        Create a new access token.

        Args:
            data: Dictionary containing the payload data

        Returns:
            The encoded JWT access token string

        Raises:
            TokenCreationError: If token creation fails
        """
        try:
            to_encode = data.copy()
            expire = datetime.now(timezone.utc) + timedelta(minutes=self._access_expire_minutes)
            to_encode.update({
                "exp": expire,
                "iat": datetime.now(timezone.utc),
                "type": "access"
            })
        except Exception as e:
            raise TokenCreationError(f"Failed to create access token: {str(e)}", e)
        else:
            return jwt.encode(to_encode, self._access_secret, algorithm=self._algorithm)

    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """
        Create a new refresh token.

        Args:
            data: Dictionary containing the payload data

        Returns:
            The encoded JWT refresh token string

        Raises:
            TokenCreationError: If token creation fails
        """
        try:
            to_encode = data.copy()
            expire = datetime.now(timezone.utc) + timedelta(minutes=self._refresh_expire_minutes)
            to_encode.update({
                "exp": expire,
                "iat": datetime.now(timezone.utc),
                "type": "refresh"
            })
        except Exception as e:
            raise TokenCreationError(f"Failed to create refresh token: {str(e)}", e)
        else:
            return jwt.encode(to_encode, self._refresh_secret, algorithm=self._algorithm)

    def verify_access_token(self, token: str) -> Dict[str, Any]:
        """
        Verify and decode an access token.

        Args:
            token: The JWT access token to verify

        Returns:
            The decoded payload

        Raises:
            EmptyTokenError: If token is empty or None
            ExpiredTokenError: If token is expired
            InvalidTokenError: If token is invalid or malformed
            TokenSignatureError: If token signature is invalid
            InvalidTokenTypeError: If token type is not 'access'
            TokenVerificationError: If verification fails for other reasons
        """
        if not token or not token.strip():
            raise EmptyTokenError("Token is empty or None")

        try:
            payload = jwt.decode(token, self._access_secret, algorithms=[self._algorithm])

            if payload.get("type") != "access":
                raise InvalidTokenTypeError("Token type must be 'access'")
        except ExpiredSignatureError as e:
            raise ExpiredTokenError("Access token has expired", e)
        except JWSSignatureError as e:
            raise TokenSignatureError("Invalid token signature", e)
        except JWTClaimsError as e:
            raise InvalidTokenError("Invalid token claims", e)
        except JWTError as e:
            raise InvalidTokenError("Invalid token format", e)
        except Exception as e:
            raise TokenVerificationError(f"Failed to verify access token: {str(e)}", e)
        else:
            return payload

    def verify_refresh_token(self, token: str) -> Dict[str, Any]:
        """
        Verify and decode a refresh token.

        Args:
            token: The JWT refresh token to verify

        Returns:
            The decoded payload

        Raises:
            EmptyTokenError: If token is empty or None
            ExpiredTokenError: If token is expired
            InvalidTokenError: If token is invalid or malformed
            TokenSignatureError: If token signature is invalid
            InvalidTokenTypeError: If token type is not 'refresh'
            TokenVerificationError: If verification fails for other reasons
        """
        if not token or not token.strip():
            raise EmptyTokenError("Token is empty or None")

        try:
            payload = jwt.decode(token, self._refresh_secret, algorithms=[self._algorithm])

            if payload.get("type") != "refresh":
                raise InvalidTokenTypeError("Token type must be 'refresh'")
        except ExpiredSignatureError as e:
            raise ExpiredTokenError("Refresh token has expired", e)
        except JWSSignatureError as e:
            raise TokenSignatureError("Invalid token signature", e)
        except JWTClaimsError as e:
            raise InvalidTokenError("Invalid token claims", e)
        except JWTError as e:
            raise InvalidTokenError("Invalid token format", e)
        except Exception as e:
            raise TokenVerificationError(f"Failed to verify refresh token: {str(e)}", e)
        else:
            return payload

    def get_token_expiration(self, token: str) -> datetime:
        """
        Get the expiration time of a token.

        Args:
            token: The JWT token

        Returns:
            The expiration datetime

        Raises:
            EmptyTokenError: If token is empty or None
            InvalidTokenError: If token is invalid or malformed
            TokenVerificationError: If token doesn't contain expiration
        """
        if not token or not token.strip():
            raise EmptyTokenError("Token is empty or None")

        try:
            payload = jwt.get_unverified_claims(token)
            exp_timestamp = payload.get("exp")

            if not exp_timestamp:
                raise TokenVerificationError("Token doesn't contain expiration information")
        except JWTError as e:
            raise InvalidTokenError("Invalid token format", e)
        except Exception as e:
            raise TokenVerificationError(f"Failed to get token expiration: {str(e)}", e)
        else:
            return datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
