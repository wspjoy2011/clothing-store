"""Password management implementation using passlib and bcrypt"""

from passlib.context import CryptContext
from passlib.exc import (
    PasswordValueError,
    PasswordSizeError,
    PasswordTruncateError,
    UnknownHashError,
    MissingBackendError,
    InternalBackendError,
    PasslibSecurityError,
)

from security.interfaces import PasswordManagerInterface
from security.exceptions import (
    EmptyPasswordError,
    InvalidPasswordHashError,
    PasswordTooLongError,
    HashingError,
    VerificationError,
    HashContextError
)


class PasswordManager(PasswordManagerInterface):
    """Password manager using bcrypt for hashing and verification"""

    def __init__(self):
        """Initialize password manager with argon2 context"""
        try:
            self._pwd_context = CryptContext(
                schemes=["argon2"],
                deprecated="auto",
                argon2__memory_cost=65536,
                argon2__time_cost=3,
                argon2__parallelism=1
            )
        except (MissingBackendError, InternalBackendError, PasslibSecurityError) as e:
            raise HashContextError("Failed to initialize password context", e)

    def hash_password(self, password: str) -> str:
        """
        Hash a plain text password using bcrypt

        Args:
            password: Plain text password to hash

        Returns:
            Hashed password string

        Raises:
            EmptyPasswordError: If password is empty or None
            PasswordTooLongError: If password exceeds maximum allowed length
            HashingError: If hashing fails for other reasons
        """
        if not password:
            raise EmptyPasswordError("Password cannot be empty or None")

        try:
            return self._pwd_context.hash(password)
        except (PasswordSizeError, PasswordTruncateError) as e:
            raise PasswordTooLongError(f"Password exceeds maximum allowed length: {e}", e)
        except PasswordValueError as e:
            raise HashingError(f"Invalid password value: {e}", e)
        except (MissingBackendError, InternalBackendError, PasslibSecurityError) as e:
            raise HashingError(f"Backend error during password hashing: {e}", e)
        except Exception as e:
            raise HashingError(f"Unexpected error during password hashing: {e}", e)

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
            VerificationError: If verification fails for other reasons
        """
        if not plain_password:
            raise EmptyPasswordError("Plain password cannot be empty or None")

        if not hashed_password:
            raise EmptyPasswordError("Hashed password cannot be empty or None")

        try:
            return self._pwd_context.verify(plain_password, hashed_password)
        except ValueError as e:
            if "not a valid" in str(e) or "malformed" in str(e):
                raise InvalidPasswordHashError(f"Invalid password hash format: {e}", e)
            raise VerificationError(f"Password verification failed: {e}", e)
        except (PasswordSizeError, PasswordTruncateError) as e:
            raise PasswordTooLongError(f"Password exceeds maximum allowed length: {e}", e)
        except (MissingBackendError, InternalBackendError, PasslibSecurityError) as e:
            raise VerificationError(f"Backend error during password verification: {e}", e)
        except Exception as e:
            raise VerificationError(f"Unexpected error during password verification: {e}", e)

    def needs_update(self, hashed_password: str) -> bool:
        """
        Check if a hashed password needs to be updated (rehashed)

        This is useful when security settings change (e.g., increasing rounds)

        Args:
            hashed_password: Hashed password to check

        Returns:
            True if password needs update, False otherwise

        Raises:
            EmptyPasswordError: If hashed password is empty or None
        """
        if not hashed_password:
            raise EmptyPasswordError("Hashed password cannot be empty or None")

        try:
            return self._pwd_context.needs_update(hashed_password)
        except ValueError:
            return True
        except (UnknownHashError, PasswordValueError):
            return True
        except Exception:
            return True

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
        if not hashed_password:
            raise EmptyPasswordError("Hashed password cannot be empty or None")

        try:
            scheme = self._pwd_context.identify(hashed_password)
            if scheme:
                return {"scheme": scheme}
            else:
                raise InvalidPasswordHashError("Unable to identify password hash scheme")
        except ValueError as e:
            if "not a valid" in str(e) or "malformed" in str(e):
                raise InvalidPasswordHashError(f"Invalid password hash format: {e}", e)
            raise InvalidPasswordHashError(f"Failed to analyze password hash: {e}", e)
        except Exception as e:
            raise InvalidPasswordHashError(f"Unexpected error analyzing password hash: {e}", e)

    def is_hash_supported(self, hashed_password: str) -> bool:
        """
        Check if a hashed password is supported by current context

        Args:
            hashed_password: Hashed password to check

        Returns:
            True if hash is supported, False otherwise
        """
        if not hashed_password:
            return False

        try:
            scheme = self._pwd_context.identify(hashed_password)
            return scheme is not None
        except Exception:
            return False
