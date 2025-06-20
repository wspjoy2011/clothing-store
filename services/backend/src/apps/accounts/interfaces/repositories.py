from abc import ABC, abstractmethod
from typing import Optional, List

from apps.accounts.dto.users import (
    UserDTO,
    UserWithProfileDTO,
    UserGroupDTO,
    UserProfileDTO,
    CreateUserDTO
)
from apps.accounts.dto.tokens import (
    ActivationTokenDTO,
    PasswordResetTokenDTO,
    RefreshTokenDTO,
    CreateTokenDTO
)


class UserRepositoryInterface(ABC):
    """Interface for user repository operations"""

    @abstractmethod
    async def get_user_by_id(self, user_id: int) -> Optional[UserDTO]:
        """
        Get a single user by ID

        Args:
            user_id: The ID of the user to retrieve

        Returns:
            UserDTO if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_user_by_email(self, email: str) -> Optional[UserDTO]:
        """
        Get a single user by email

        Args:
            email: The email of the user to retrieve

        Returns:
            UserDTO if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_user_with_profile_by_id(self, user_id: int) -> Optional[UserWithProfileDTO]:
        """
        Get a user with profile information by ID

        Args:
            user_id: The ID of the user to retrieve

        Returns:
            UserWithProfileDTO if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_user_with_profile_by_email(self, email: str) -> Optional[UserWithProfileDTO]:
        """
        Get a user with profile information by email

        Args:
            email: The email of the user to retrieve

        Returns:
            UserWithProfileDTO if found, None otherwise
        """
        pass

    @abstractmethod
    async def create_user(self, user_data: CreateUserDTO) -> UserDTO:
        """
        Create a new user

        Args:
            user_data: Data for creating the user

        Returns:
            Created UserDTO
        """
        pass

    @abstractmethod
    async def update_user_status(self, user_id: int, is_active: bool) -> bool:
        """
        Update user active status

        Args:
            user_id: ID of the user to update
            is_active: New active status

        Returns:
            True if updated successfully, False otherwise
        """
        pass

    @abstractmethod
    async def update_user_password(self, user_id: int, hashed_password: str) -> bool:
        """
        Update user password

        Args:
            user_id: ID of the user to update
            hashed_password: New hashed password

        Returns:
            True if updated successfully, False otherwise
        """
        pass

    @abstractmethod
    async def delete_user(self, user_id: int) -> bool:
        """
        Delete a user

        Args:
            user_id: ID of the user to delete

        Returns:
            True if deleted successfully, False otherwise
        """
        pass

    @abstractmethod
    async def get_users_list(self, limit: int = 50, offset: int = 0) -> List[UserWithProfileDTO]:
        """
        Get list of users with pagination

        Args:
            limit: Maximum number of users to return
            offset: Number of users to skip

        Returns:
            List of UserWithProfileDTO
        """
        pass

    @abstractmethod
    async def get_users_count(self) -> int:
        """
        Get total count of users

        Returns:
            Number of users in the database
        """
        pass


class UserGroupRepositoryInterface(ABC):
    """Interface for user group repository operations"""

    @abstractmethod
    async def get_all_groups(self) -> List[UserGroupDTO]:
        """
        Get all user groups

        Returns:
            List of UserGroupDTO
        """
        pass

    @abstractmethod
    async def get_group_by_id(self, group_id: int) -> Optional[UserGroupDTO]:
        """
        Get user group by ID

        Args:
            group_id: ID of the group to retrieve

        Returns:
            UserGroupDTO if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_group_by_name(self, name: str) -> Optional[UserGroupDTO]:
        """
        Get user group by name

        Args:
            name: Name of the group to retrieve

        Returns:
            UserGroupDTO if found, None otherwise
        """
        pass


class UserProfileRepositoryInterface(ABC):
    """Interface for user profile repository operations"""

    @abstractmethod
    async def get_profile_by_user_id(self, user_id: int) -> Optional[UserProfileDTO]:
        """
        Get user profile by user ID

        Args:
            user_id: ID of the user

        Returns:
            UserProfileDTO if found, None otherwise
        """
        pass

    @abstractmethod
    async def create_profile(self, user_id: int, profile_data: dict) -> UserProfileDTO:
        """
        Create user profile

        Args:
            user_id: ID of the user
            profile_data: Profile data

        Returns:
            Created UserProfileDTO
        """
        pass

    @abstractmethod
    async def update_profile(self, user_id: int, profile_data: dict) -> Optional[UserProfileDTO]:
        """
        Update user profile

        Args:
            user_id: ID of the user
            profile_data: Updated profile data

        Returns:
            Updated UserProfileDTO if successful, None otherwise
        """
        pass

    @abstractmethod
    async def delete_profile(self, user_id: int) -> bool:
        """
        Delete user profile

        Args:
            user_id: ID of the user

        Returns:
            True if deleted successfully, False otherwise
        """
        pass


class TokenRepositoryInterface(ABC):
    """Interface for token repository operations"""

    @abstractmethod
    async def get_activation_token_by_token(self, token: str) -> Optional[ActivationTokenDTO]:
        """Get activation token by token string"""
        pass

    @abstractmethod
    async def get_activation_token_by_user_id(self, user_id: int) -> Optional[ActivationTokenDTO]:
        """Get activation token by user ID"""
        pass

    @abstractmethod
    async def get_activation_token_by_email_and_token(self, email: str, token: str) -> Optional[ActivationTokenDTO]:
        """Get activation token by email and token combination"""
        pass

    @abstractmethod
    async def create_activation_token(self, token_data: CreateTokenDTO) -> ActivationTokenDTO:
        """Create activation token"""
        pass

    @abstractmethod
    async def delete_activation_token(self, token: str) -> bool:
        """Delete activation token"""
        pass

    @abstractmethod
    async def delete_activation_tokens_by_user_id(self, user_id: int) -> bool:
        """Delete all activation tokens for user"""
        pass

    @abstractmethod
    async def get_password_reset_token_by_token(self, token: str) -> Optional[PasswordResetTokenDTO]:
        """Get password reset token by token string"""
        pass

    @abstractmethod
    async def get_password_reset_token_by_user_id(self, user_id: int) -> Optional[PasswordResetTokenDTO]:
        """Get password reset token by user ID"""
        pass

    @abstractmethod
    async def create_password_reset_token(self, token_data: CreateTokenDTO) -> PasswordResetTokenDTO:
        """Create password reset token"""
        pass

    @abstractmethod
    async def delete_password_reset_token(self, token: str) -> bool:
        """Delete password reset token"""
        pass

    @abstractmethod
    async def get_refresh_token_by_token(self, token: str) -> Optional[RefreshTokenDTO]:
        """Get refresh token by token string"""
        pass

    @abstractmethod
    async def get_refresh_tokens_by_user_id(self, user_id: int) -> List[RefreshTokenDTO]:
        """Get all refresh tokens for user"""
        pass

    @abstractmethod
    async def create_refresh_token(self, token_data: CreateTokenDTO) -> RefreshTokenDTO:
        """Create refresh token"""
        pass

    @abstractmethod
    async def delete_refresh_token(self, token: str) -> bool:
        """Delete refresh token"""
        pass

    @abstractmethod
    async def delete_expired_tokens(self) -> int:
        """Delete all expired tokens"""
        pass

    @abstractmethod
    async def delete_user_refresh_tokens(self, user_id: int) -> int:
        """Delete all refresh tokens for user"""
        pass
