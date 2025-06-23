"""Interfaces for account services"""

from abc import ABC, abstractmethod

from apps.accounts.dto.users import UserDTO, CreateUserDTO, UserLoginDTO, LoginResponseDTO
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

    @abstractmethod
    async def login_user(self, login_data: UserLoginDTO) -> LoginResponseDTO:
        """
        Authenticate user and generate JWT tokens

        Args:
            login_data: User login credentials (email and password)

        Returns:
            LoginResponseDTO with access and refresh tokens

        Raises:
            UserNotFoundError: If user with given email is not found
            UserInactiveError: If user account is not activated
            InvalidCredentialsError: If password is incorrect
            TokenGenerationError: If JWT token generation fails
            LoginError: If login fails for other reasons
        """
        pass

    @abstractmethod
    async def logout_user(self, refresh_token: str) -> None:
        """
        Logout user by removing refresh token from database

        Args:
            refresh_token: Refresh token to be removed

        Returns:
            None - always succeeds, no exceptions raised even if token doesn't exist
        """
        pass

    @abstractmethod
    async def get_user_by_refresh_token(self, refresh_token: str) -> UserDTO:
        """
        Get user information by refresh token

        Args:
            refresh_token: Valid refresh token

        Returns:
            UserDTO with user information

        Raises:
            InvalidRefreshTokenError: If refresh token is invalid or expired
            UserNotFoundError: If user associated with token is not found
            TokenValidationError: If token validation fails
        """
        pass
