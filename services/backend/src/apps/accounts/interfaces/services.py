"""Interfaces for account services"""

from abc import ABC, abstractmethod

from apps.accounts.dto.users import UserDTO, CreateUserDTO
from apps.accounts.dto.activation import ActivateAccountDTO


class AccountServiceInterface(ABC):
    """Interface for account service operations"""

    @abstractmethod
    async def register_user(self, user_data: CreateUserDTO) -> UserDTO:
        """
        Register a new user with default group assignment and create activation token

        Args:
            user_data: User registration data with plain text password (no group_id)

        Returns:
            Created UserDTO with hashed password and assigned group

        Raises:
            EmailAlreadyExistsError: If email already exists
            UserCreationError: If user creation fails at service level or default group not found
            UserPasswordError: Password processing errors
        """
        pass

    @abstractmethod
    async def activate_account(self, activation_data: ActivateAccountDTO) -> UserDTO:
        """
        Activate user account using email and activation token

        Args:
            activation_data: Activation data containing email and token

        Returns:
            Activated UserDTO

        Raises:
            UserNotFoundError: If user with given email is not found
            UserAlreadyActivatedError: If user is already activated
            InvalidActivationTokenError: If token doesn't match the user
            ExpiredActivationTokenError: If activation token has expired
        """
        pass

    @abstractmethod
    async def resend_activation_email(self, email: str) -> bool:
        """
        Resend activation email for existing user

        Deletes any existing activation tokens and creates a new one

        Args:
            email: User email address

        Returns:
            True if email was sent successfully

        Raises:
            UserNotFoundError: If user with given email is not found
            UserAlreadyActivatedError: If user is already activated
            TokenCreationError: If token creation fails
            BaseEmailError: If email sending fails
        """
        pass
