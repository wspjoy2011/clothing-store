"""Schemas for password reset operations"""

from pydantic import BaseModel, EmailStr, field_validator

from apps.accounts.validators.password import (
    validate_password_strength,
    validate_password_format
)


class PasswordResetRequestSchema(BaseModel):
    """Schema for password reset request"""
    email: EmailStr

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        return value.lower()


class PasswordResetRequestResponseSchema(BaseModel):
    """Schema for password reset request response"""
    message: str = "Password reset request processed successfully"
    email: str

    model_config = {
        "from_attributes": True
    }


class PasswordResetConfirmSchema(BaseModel):
    """Schema for password reset confirmation"""
    token: str
    new_password: str

    @field_validator("token")
    @classmethod
    def validate_token(cls, value):
        if not value or not value.strip():
            raise ValueError("Token cannot be empty")
        return value.strip()

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, value):
        validate_password_format(value)
        validate_password_strength(value)
        return value


class PasswordResetConfirmResponseSchema(BaseModel):
    """Schema for password reset confirmation response"""
    message: str = "Password reset completed successfully"

    model_config = {
        "from_attributes": True
    }
