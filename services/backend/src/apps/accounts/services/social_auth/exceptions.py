"""
Exceptions for social authentication service.
"""


class SocialAuthError(Exception):
    """Base exception for social authentication errors."""

    def __init__(self, message: str, provider: str = "", original_error: Exception = None):
        super().__init__(message)
        self.provider = provider
        self.original_error = original_error


class SocialProviderError(SocialAuthError):
    """Raised when OAuth provider returns an error."""
    pass


class SocialTokenError(SocialAuthError):
    """Raised when social token verification fails."""

    def __init__(self, message: str, provider: str = "", status_code: int = 401, original_error: Exception = None):
        super().__init__(message, provider, original_error)
        self.status_code = status_code


class SocialUserInfoError(SocialAuthError):
    """Raised when extracting user info from social provider fails."""

    def __init__(self, message: str, provider: str = "", missing_fields: list[str] = None,
                 original_error: Exception = None):
        super().__init__(message, provider, original_error)
        self.missing_fields = missing_fields or []


class SocialUserValidationError(SocialAuthError):
    """Raised when social user profile validation fails."""
    pass


class SocialConfigurationError(SocialAuthError):
    """Raised when social authentication configuration is invalid."""
    pass


class SocialUserLookupError(SocialAuthError):
    """Raised when user lookup in database fails."""
    pass


class SocialTokenGenerationError(SocialAuthError):
    """Raised when JWT token generation fails for social user."""
    pass
