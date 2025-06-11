from dataclasses import dataclass
from datetime import datetime


@dataclass
class TokenDTO:
    """Base data transfer object for tokens"""
    id: int
    token: str
    expires_at: datetime
    user_id: int


@dataclass(kw_only=True)
class ActivationTokenDTO(TokenDTO):
    """Data transfer object for activation token"""
    pass


@dataclass(kw_only=True)
class PasswordResetTokenDTO(TokenDTO):
    """Data transfer object for password reset token"""
    pass


@dataclass(kw_only=True)
class RefreshTokenDTO(TokenDTO):
    """Data transfer object for refresh token"""
    pass


@dataclass
class CreateTokenDTO:
    """Data transfer object for creating a new token"""
    token: str
    expires_at: datetime
    user_id: int
