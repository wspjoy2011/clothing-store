class CheckoutRepositoryError(Exception):
    """Base exception for checkout storage failures"""

    def __init__(self, message: str, original_error: Exception = None):
        self.message = message
        self.original_error = original_error
        super().__init__(message)


class CartStorageError(CheckoutRepositoryError):
    """Raised when a cart statement could not be carried out at all"""
