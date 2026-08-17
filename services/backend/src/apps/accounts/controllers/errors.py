"""What the client is told for each domain failure.

The message describes the outcome of the requested action. The cause stays in the
log of the layer that knows it: an exception text written for us leaks internal
identifiers, statement names and storage details when it reaches a response body.
"""

from apps.accounts.services.exceptions import (
    EmailAlreadyExistsError,
    ExpiredActivationTokenError,
    ExpiredPasswordResetTokenError,
    IncorrectCurrentPasswordError,
    InvalidActivationTokenError,
    InvalidCredentialsError,
    InvalidPasswordResetTokenError,
    InvalidRefreshTokenError,
    LoginError,
    PasswordChangeError,
    PasswordResetEmailError,
    PasswordResetError,
    PasswordResetRollbackError,
    PasswordResetTokenNotFoundError,
    SamePasswordError,
    TokenGenerationError,
    TokenValidationError,
    UserAlreadyActivatedError,
    UserCreationError,
    UserInactiveError,
    UserNotFoundError,
    UserPasswordError,
)

GENERIC_MESSAGE = "The request could not be completed. Please try again."

# Registration and activation
CLIENT_MESSAGES = {
    EmailAlreadyExistsError: "This email is already registered.",
    UserCreationError: "Registration could not be completed. Please try again.",
    UserPasswordError: "The password does not meet the requirements.",
    UserAlreadyActivatedError: "This account is already active.",
    InvalidActivationTokenError: "This activation link is not valid.",
    ExpiredActivationTokenError: "This activation link has expired. Please request a new one.",

    # Authentication
    InvalidCredentialsError: "Invalid email or password.",
    UserInactiveError: "Invalid email or password.",
    UserNotFoundError: "Invalid email or password.",
    LoginError: "Sign-in could not be completed. Please try again.",
    TokenGenerationError: "Sign-in could not be completed. Please try again.",
    InvalidRefreshTokenError: "This session has expired. Please sign in again.",
    TokenValidationError: "This session has expired. Please sign in again.",

    # Password reset and change
    InvalidPasswordResetTokenError: "This password reset link is not valid.",
    ExpiredPasswordResetTokenError: "This password reset link has expired. Please request a new one.",
    PasswordResetTokenNotFoundError: "This password reset link is not valid or has already been used.",
    PasswordResetError: "The password could not be reset. Please request a new link.",
    PasswordResetEmailError: "The password reset email could not be sent. Please try again.",
    PasswordResetRollbackError: "The password reset could not be completed. Please request it again.",
    IncorrectCurrentPasswordError: "The current password is incorrect.",
    SamePasswordError: "The new password must differ from the current one.",
    PasswordChangeError: "The password could not be changed. Please try again.",
}


def client_message(error: Exception) -> str:
    """
    Get the message the client is allowed to see for a failure

    Args:
        error: Domain exception raised by the service

    Returns:
        Message describing the outcome, never the cause
    """
    for error_type, message in CLIENT_MESSAGES.items():
        if isinstance(error, error_type):
            return message

    return GENERIC_MESSAGE
