"""Interfaces for security components"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any


class PasswordManagerInterface(ABC):
    """Interface for password management operations"""

    @abstractmethod
    def hash_password(self, password: str) -> str:
        """
        Hash a plain text password

        Args:
            password: Plain text password to hash

        Returns:
            Hashed password string

        Raises:
            EmptyPasswordError: If password is empty or None
            PasswordTooLongError: If password exceeds maximum allowed length
            HashingError: If hashing fails
        """
        pass

    @abstractmethod
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain text password against a hashed password

        Args:
            plain_password: Plain text password to verify
            hashed_password: Hashed password to compare against

        Returns:
            True if password matches, False otherwise

        Raises:
            EmptyPasswordError: If either password is empty or None
            InvalidPasswordHashError: If hashed password format is invalid
            VerificationError: If verification fails
        """
        pass

    @abstractmethod
    def needs_update(self, hashed_password: str) -> bool:
        """
        Check if a hashed password needs to be updated (rehashed)

        Args:
            hashed_password: Hashed password to check

        Returns:
            True if password needs update, False otherwise

        Raises:
            EmptyPasswordError: If hashed password is empty or None
        """
        pass

    @abstractmethod
    def get_hash_info(self, hashed_password: str) -> dict:
        """
        Get information about a hashed password

        Args:
            hashed_password: Hashed password to analyze

        Returns:
            Dictionary with hash information (scheme, rounds, etc.)

        Raises:
            EmptyPasswordError: If hashed password is empty or None
            InvalidPasswordHashError: If hashed password format is invalid
        """
        pass

    @abstractmethod
    def is_hash_supported(self, hashed_password: str) -> bool:
        """
        Check if a hashed password is supported by current context

        Args:
            hashed_password: Hashed password to check

        Returns:
            True if hash is supported, False otherwise
        """
        pass


class JWTManagerInterface(ABC):
    """Interface for JWT token management operations."""

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass

    @abstractmethod
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
        pass
