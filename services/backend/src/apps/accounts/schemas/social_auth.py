"""
Pydantic schemas for social authentication API.
"""

from typing import Optional
from pydantic import BaseModel, Field, field_validator
from email_validator import validate_email, EmailNotValidError


class SocialAuthRequestSchema(BaseModel):
    """
    Schema for social authentication request.
    """
    provider: str = Field(
        ...,
        description="OAuth provider name (google, facebook, etc.)",
        min_length=1,
        max_length=50
    )
    access_token: str = Field(
        ...,
        description="OAuth access token from frontend",
        min_length=1,
        max_length=2048
    )

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, value: str) -> str:
        """Validate and normalize provider name."""
        if not value or not value.strip():
            raise ValueError("Provider name cannot be empty")

        provider = value.strip().lower()

        supported_providers = ["google", "facebook", "github", "discord"]

        if provider not in supported_providers:
            raise ValueError(
                f"Unsupported provider '{provider}'. "
                f"Supported providers: {', '.join(supported_providers)}"
            )

        return provider

    @field_validator("access_token")
    @classmethod
    def validate_access_token(cls, value: str) -> str:
        """Validate access token format."""
        if not value or not value.strip():
            raise ValueError("Access token cannot be empty")

        token = value.strip()

        if len(token) < 10:
            raise ValueError("Access token is too short")

        if any(char in token for char in ['\n', '\r', '\t']):
            raise ValueError("Access token contains invalid characters")

        return token


class SocialUserProfileSchema(BaseModel):
    """
    Schema for social user profile data.
    """
    provider: str = Field(..., description="OAuth provider name")
    provider_id: str = Field(..., description="User ID from OAuth provider")
    email: str = Field(..., description="User email address")
    name: str = Field(..., description="User full name")
    first_name: Optional[str] = Field(None, description="User first name")
    last_name: Optional[str] = Field(None, description="User last name")
    avatar_url: Optional[str] = Field(None, description="User avatar URL")
    locale: Optional[str] = Field(None, description="User locale/language")
    verified_email: bool = Field(True, description="Is email verified by provider")

    @field_validator("email")
    @classmethod
    def validate_email_field(cls, value: str) -> str:
        """Validate and normalize email address."""
        try:
            validation_result = validate_email(value)
            return validation_result.email
        except EmailNotValidError as e:
            raise ValueError(f"Invalid email format: {str(e)}")

    @field_validator("avatar_url")
    @classmethod
    def validate_avatar_url(cls, value: Optional[str]) -> Optional[str]:
        """Validate avatar URL format."""
        if not value:
            return None

        if not value.startswith(('http://', 'https://')):
            raise ValueError("Avatar URL must start with http:// or https://")

        return value


class SocialAuthTokensSchema(BaseModel):
    """
    Schema for JWT tokens response.
    """
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(default=3600, description="Token expiration time in seconds")


class SocialAuthResponseSchema(BaseModel):
    """
    Schema for social authentication response.
    """
    success: bool = Field(..., description="Authentication success status")
    tokens: Optional[SocialAuthTokensSchema] = Field(None, description="JWT tokens")
    user_profile: Optional[SocialUserProfileSchema] = Field(None, description="User profile data")
    is_new_user: bool = Field(False, description="Is this a new user registration")
    message: str = Field("", description="Response message")
    provider: str = Field("", description="OAuth provider used")


class SocialAuthErrorSchema(BaseModel):
    """
    Schema for social authentication error response.
    """
    success: bool = Field(False, description="Authentication success status")
    error_type: str = Field(..., description="Type of error")
    error_message: str = Field(..., description="Error message")
    provider: str = Field("", description="OAuth provider")
    details: Optional[dict] = Field(None, description="Additional error details")


class SupportedProvidersSchema(BaseModel):
    """
    Schema for supported providers response.
    """
    providers: list[str] = Field(..., description="List of supported OAuth providers")
    total_count: int = Field(..., description="Total number of supported providers")
