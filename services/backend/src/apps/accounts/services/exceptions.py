"""Account service exceptions - business logic errors for registration scenarios"""


class AccountServiceError(Exception):
    """Base exception for all account service errors"""

    def __init__(self, message: str, original_error: Exception = None):
        super().__init__(message)
        self.original_error = original_error


class RegistrationError(AccountServiceError):
    """Base exception for user registration operations"""
    pass


class EmailAlreadyExistsError(RegistrationError):
    """Raised when trying to create a user with an email that already exists"""
    pass


class UserCreationError(RegistrationError):
    """Raised when user creation fails at service level"""
    pass


class InvalidGroupError(RegistrationError):
    """Raised when specified user group is invalid or doesn't exist"""
    pass


class UserPasswordError(RegistrationError):
    """Raised when password-related operations fail during registration"""
    pass


class ActivationError(AccountServiceError):
    """Base exception for user activation operations"""
    pass


class UserNotFoundError(ActivationError):
    """Raised when user is not found by email"""
    pass


class UserAlreadyActivatedError(ActivationError):
    """Raised when trying to activate an already activated user"""
    pass


class InvalidActivationTokenError(ActivationError):
    """Raised when activation token is invalid or doesn't match the user"""
    pass


class ExpiredActivationTokenError(ActivationError):
    """Raised when activation token has expired"""
    pass


class AuthenticationError(AccountServiceError):
    """Base exception for authentication operations"""
    pass


class InvalidCredentialsError(AuthenticationError):
    """Raised when login credentials are invalid"""
    pass


class UserInactiveError(AuthenticationError):
    """Raised when user tries to login but account is not activated"""
    pass


class LoginError(AuthenticationError):
    """Raised when login fails for general reasons"""
    pass


class TokenGenerationError(AuthenticationError):
    """Raised when JWT token generation fails during login"""
    pass


class InvalidRefreshTokenError(AccountServiceError):
    """Raised when refresh token is invalid or expired"""
    pass


class TokenValidationError(AccountServiceError):
    """Raised when token validation fails"""
    pass
