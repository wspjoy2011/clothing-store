from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional


@dataclass
class UserGroupDTO:
    """Data transfer object for user group"""
    id: int
    name: str


@dataclass
class UserDTO:
    """Data transfer object for user"""
    id: int
    email: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    group_id: int
    group_name: str


@dataclass
class UserWithProfileDTO:
    """Data transfer object for user with profile information"""
    id: int
    email: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    group_id: int
    group_name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None
    info: Optional[str] = None


@dataclass
class UserProfileDTO:
    """Data transfer object for user profile"""
    id: int
    first_name: Optional[str]
    last_name: Optional[str]
    avatar: Optional[str]
    gender: Optional[str]
    date_of_birth: Optional[date]
    info: Optional[str]
    user_id: int


@dataclass
class CreateUserDTO:
    """Data transfer object for creating a new user"""
    email: str
    password: str
    group_id: Optional[int] = None


@dataclass
class UserLoginDTO:
    """Data transfer object for user login"""
    email: str
    password: str


@dataclass
class LoginResponseDTO:
    """Data transfer object for login response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
