"""Repository-level exceptions for accounts app"""


class AccountsBaseRepositoryError(Exception):
    """Base exception for all accounts repository-related errors"""

    def __init__(self, message: str, original_error: Exception = None):
        super().__init__(message)
        self.original_error = original_error


class DatabaseQueryError(AccountsBaseRepositoryError):
    """Raised when database query execution fails"""
    pass


class UserRepositoryError(AccountsBaseRepositoryError):
    """Base exception for user repository operations"""
    pass


class UserNotFoundError(UserRepositoryError):
    """Raised when user is not found"""
    pass


class UserCreationError(UserRepositoryError):
    """Raised when user creation fails"""
    pass


class UserUpdateError(UserRepositoryError):
    """Raised when user update fails"""
    pass


class UserDeletionError(UserRepositoryError):
    """Raised when user deletion fails"""
    pass


class ProfileRepositoryError(AccountsBaseRepositoryError):
    """Base exception for profile repository operations"""
    pass


class ProfileNotFoundError(ProfileRepositoryError):
    """Raised when profile is not found"""
    pass


class ProfileCreationError(ProfileRepositoryError):
    """Raised when profile creation fails"""
    pass


class ProfileUpdateError(ProfileRepositoryError):
    """Raised when profile update fails"""
    pass


class ProfileDeletionError(ProfileRepositoryError):
    """Raised when profile deletion fails"""
    pass


class TokenRepositoryError(AccountsBaseRepositoryError):
    """Base exception for token repository operations"""
    pass


class TokenNotFoundError(TokenRepositoryError):
    """Raised when token is not found"""
    pass


class TokenCreationError(TokenRepositoryError):
    """Raised when token creation fails"""
    pass


class TokenDeletionError(TokenRepositoryError):
    """Raised when token deletion fails"""
    pass


class GroupRepositoryError(AccountsBaseRepositoryError):
    """Base exception for group repository operations"""
    pass


class GroupNotFoundError(GroupRepositoryError):
    """Raised when group is not found"""
    pass
