"""
DTO for social authentication service.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class SocialAuthRequest:
    """
    Request for social authentication.
    """
    provider: str
    access_token: str


@dataclass
class SocialUserProfile:
    """
    Social user profile extracted from OAuth provider.
    """
    provider: str
    provider_id: str
    email: str
    name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None
    locale: Optional[str] = None
    verified_email: bool = True


@dataclass
class SocialAuthResult:
    """
    Result of social authentication process.
    """
    success: bool
    user_profile: Optional[SocialUserProfile] = None
    user_exists: bool = False
    user_id: Optional[int] = None
    message: str = ""
    provider: str = ""


@dataclass
class SocialAuthTokens:
    """
    JWT tokens for authenticated social user.
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 3600


@dataclass
class SocialAuthResponse:
    """
    Complete social authentication response.
    """
    success: bool
    tokens: Optional[SocialAuthTokens] = None
    user_profile: Optional[SocialUserProfile] = None
    is_new_user: bool = False
    message: str = ""
    provider: str = ""
