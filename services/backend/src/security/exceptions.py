"""Security-related exceptions"""


class SecurityError(Exception):
    """Base exception for security-related errors"""

    def __init__(self, message: str, original_error: Exception = None):
        super().__init__(message)
        self.original_error = original_error


class PasswordError(SecurityError):
    """Exception for password-related errors"""
    pass


class EmptyPasswordError(PasswordError):
    """Exception raised when password is empty or None"""
    pass


class InvalidPasswordHashError(PasswordError):
    """Exception raised when password hash is invalid or corrupted"""
    pass


class PasswordTooLongError(PasswordError):
    """Exception raised when password exceeds maximum allowed length"""
    pass


class HashingError(PasswordError):
    """Exception for password hashing errors"""
    pass


class VerificationError(PasswordError):
    """Exception for password verification errors"""
    pass


class HashContextError(SecurityError):
    """Exception for password context configuration errors"""
    pass
