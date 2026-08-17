from typing import Optional

from pydantic import BaseModel, Field


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request"""

    refresh_token: str = Field(
        ...,
        description="Valid refresh token",
        min_length=1,
        max_length=1000,
    )

    class Config:
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJlbWFpbCI6InVzZXJAZXhhbXBsZS5jb20iLCJncm91cF9pZCI6MSwiZ3JvdXBfbmFtZSI6InVzZXIiLCJleHAiOjE3MzY5NjE2MDAsImlhdCI6MTczNjg3NTIwMCwidHlwZSI6InJlZnJlc2gifQ.xyz..."
            }
        }


class RefreshTokenResponse(BaseModel):
    """Schema for refresh token response"""

    access_token: str = Field(
        ...,
        description="New access token",
    )

    refresh_token: str = Field(
        ...,
        description="New refresh token, replacing the one presented",
    )

    token_type: str = Field(
        default="bearer",
        description="Token type",
    )

    expires_in: int = Field(
        default=3600,
        description="Token expiration time in seconds",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJlbWFpbCI6InVzZXJAZXhhbXBsZS5jb20iLCJncm91cF9pZCI6MSwiZ3JvdXBfbmFtZSI6InVzZXIiLCJleHAiOjE3MzY4NzUyMDAsImlhdCI6MTczNjg3MTYwMCwidHlwZSI6ImFjY2VzcyJ9.abc123...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ0eXBlIjoicmVmcmVzaCJ9.def456...",
                "token_type": "bearer",
                "expires_in": 3600
            }
        }


class TokenErrorResponse(BaseModel):
    """Schema for token error response"""

    detail: str = Field(
        ...,
        description="Error message",
    )

    error_code: Optional[str] = Field(
        None,
        description="Specific error code",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Invalid refresh token",
                "error_code": "INVALID_REFRESH_TOKEN"
            }
        }


class JWTTokenInfo(BaseModel):
    """Schema for JWT token information"""

    user_id: int = Field(
        ...,
        description="User ID",
    )

    email: str = Field(
        ...,
        description="User email",
    )

    group_id: int = Field(
        ...,
        description="User group ID",
    )

    group_name: str = Field(
        ...,
        description="User group name",
    )

    token_type: str = Field(
        ...,
        description="Token type (access or refresh)",
    )

    expires_at: int = Field(
        ...,
        description="Token expiration timestamp",
    )

    issued_at: int = Field(
        ...,
        description="Token issued timestamp",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "email": "user@example.com",
                "group_id": 1,
                "group_name": "user",
                "token_type": "access",
                "expires_at": 1736875200,
                "issued_at": 1736871600
            }
        }
