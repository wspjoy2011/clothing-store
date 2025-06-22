from datetime import datetime

from pydantic import BaseModel, field_validator, EmailStr

from apps.accounts.validators.password import (
    validate_password_strength,
    validate_password_format
)


class CreateUserSchema(BaseModel):
    """Schema for user registration request"""
    email: EmailStr
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        return value.lower()

    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        validate_password_format(value)
        validate_password_strength(value)
        return value


class UserResponseSchema(BaseModel):
    """Schema for user data in API responses"""
    id: int
    email: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    group_id: int
    group_name: str

    model_config = {
        "from_attributes": True
    }


class CreateUserResponseSchema(BaseModel):
    """Schema for user registration response"""
    user: UserResponseSchema
    message: str = "User created successfully"

    model_config = {
        "from_attributes": True
    }


class UserLoginSchema(BaseModel):
    """Schema for user login request"""
    email: EmailStr
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value):
        return value.lower()


class LoginResponseSchema(BaseModel):
    """Schema for login response with JWT tokens"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

    model_config = {
        "from_attributes": True
    }
