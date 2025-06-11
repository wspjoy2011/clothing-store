"""Interfaces for security components"""

from abc import ABC, abstractmethod


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
