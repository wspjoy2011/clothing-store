"""Data transfer objects for password reset operations"""

from dataclasses import dataclass


@dataclass
class PasswordResetRequestDTO:
    """Data transfer object for password reset request"""
    email: str


@dataclass
class PasswordResetConfirmDTO:
    """Data transfer object for password reset confirmation"""
    token: str
    new_password: str


@dataclass
class PasswordChangeDTO:
    """Data transfer object for password change when user knows old password"""
    old_password: str
    new_password: str
