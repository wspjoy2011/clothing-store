"""Schemas for password reset operations"""

from pydantic import BaseModel, EmailStr, field_validator, model_validator

from apps.accounts.validators.password import validate_password_format, validate_password_strength


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


class PasswordChangeSchema(BaseModel):
    """Schema for password change by authenticated user"""
    old_password: str
    new_password: str

    @field_validator("old_password")
    @classmethod
    def validate_old_password(cls, value):
        if not value or not value.strip():
            raise ValueError("Current password is required")
        return value

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, value):
        validate_password_format(value)
        validate_password_strength(value)
        return value

    @model_validator(mode='after')
    def validate_passwords_different(self):
        """Validate that old and new passwords are different"""
        if self.old_password == self.new_password:
            raise ValueError("New password must be different from current password")
        return self


class PasswordChangeResponseSchema(BaseModel):
    """Schema for password change response"""
    message: str = "Password changed successfully"

    model_config = {
        "from_attributes": True
    }
