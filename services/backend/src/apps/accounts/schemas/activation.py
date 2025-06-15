from pydantic import BaseModel, field_validator, EmailStr

from apps.accounts.schemas.user import UserResponseSchema


class ActivateAccountSchema(BaseModel):
    """Schema for account activation request"""
    email: EmailStr
    token: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        """Normalize email to lowercase"""
        return value.lower()

    @field_validator("token")
    @classmethod
    def validate_token(cls, value):
        """Validate activation token format"""
        value = value.strip()

        if not value:
            raise ValueError("Token must be a non-empty string")

        return value.strip()


class ActivateAccountResponseSchema(BaseModel):
    """Schema for account activation response"""
    user: UserResponseSchema
    message: str = "Account activated successfully"

    model_config = {
        "from_attributes": True
    }


class ActivationStatusSchema(BaseModel):
    """Schema for activation status check response"""
    email: str
    is_active: bool
    requires_activation: bool
    message: str

    model_config = {
        "from_attributes": True
    }


class ResendActivationSchema(BaseModel):
    """Schema for resend activation email request"""
    email: EmailStr

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        """Normalize email to lowercase"""
        return value.lower()


class ResendActivationResponseSchema(BaseModel):
    """Schema for resend activation email response"""
    message: str = "Activation email sent successfully"
    email: str

    model_config = {
        "from_attributes": True
    }
