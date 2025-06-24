class OAuthError(Exception):
    """Base exception for OAuth-related errors."""
    pass


class TokenVerificationError(OAuthError):
    """Raised when token verification fails."""

    def __init__(self, provider: str, message: str, status_code: int = 401):
        self.provider = provider
        self.status_code = status_code
        super().__init__(f"{provider}: {message}")


class UserInfoError(OAuthError):
    """Raised when user information extraction fails."""

    def __init__(self, provider: str, message: str, missing_fields: list[str] = None):
        self.provider = provider
        self.missing_fields = missing_fields or []
        super().__init__(f"{provider}: {message}")


class ProviderNotSupportedError(OAuthError):
    """Raised when trying to use an unsupported OAuth provider."""

    def __init__(self, provider: str, supported_providers: list[str]):
        self.provider = provider
        self.supported_providers = supported_providers
        super().__init__(
            f"Provider '{provider}' is not supported. "
            f"Supported providers: {', '.join(supported_providers)}"
        )


class ConfigurationError(OAuthError):
    """Raised when OAuth provider configuration is invalid."""

    def __init__(self, provider: str, message: str):
        self.provider = provider
        super().__init__(f"{provider} configuration error: {message}")
