"""Email-related exceptions for the notifications module"""


class BaseEmailError(Exception):
    """Base exception for all email-related errors"""

    def __init__(self, message: str, original_error: Exception = None):
        super().__init__(message)
        self.message = message
        self.original_error = original_error

    def __str__(self) -> str:
        return self.message


class EmailConnectionError(BaseEmailError):
    """Raised when unable to connect to the email server"""
    pass


class EmailAuthenticationError(BaseEmailError):
    """Raised when email authentication fails"""
    pass


class EmailSendError(BaseEmailError):
    """Raised when email sending fails"""
    pass


class EmailTemplateError(BaseEmailError):
    """Raised when email template processing fails"""
    pass
