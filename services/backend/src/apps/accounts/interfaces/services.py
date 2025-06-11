# src/apps/accounts/interfaces/services.py
"""Interfaces for account services"""

from abc import ABC, abstractmethod
from apps.accounts.dto.users import UserDTO, CreateUserDTO


class AccountServiceInterface(ABC):
    """Interface for account service operations"""

    @abstractmethod
    async def register_user(self, user_data: CreateUserDTO) -> UserDTO:
        """
        Register a new user

        Args:
            user_data: User registration data with plain text password

        Returns:
            Created UserDTO with hashed password

        Raises:
            EmailAlreadyExistsError: If email already exists
            UserCreationError: If user creation fails at service level
            EmptyPasswordError: If password is empty or None (from password manager)
            PasswordTooLongError: If password exceeds maximum allowed length (from password manager)
            HashingError: If password hashing fails (from password manager)
        """
        pass
