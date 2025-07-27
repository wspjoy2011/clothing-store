"""Service layer exceptions for checkout operations"""


class CheckoutServiceError(Exception):
    """Base exception for checkout service errors"""

    def __init__(self, message: str, original_error: Exception = None):
        super().__init__(message)
        self.message = message
        self.original_error = original_error


class CartTokenCreationError(CheckoutServiceError):
    """Raised when cart token creation fails"""
    pass


class CartNotFoundError(CheckoutServiceError):
    """Raised when cart is not found"""
    pass


class CartItemNotFoundError(CheckoutServiceError):
    """Raised when cart item is not found"""
    pass


class ProductNotFoundError(CheckoutServiceError):
    """Raised when product is not found"""
    pass


class InsufficientStockError(CheckoutServiceError):
    """Raised when there is insufficient stock for the requested quantity"""
    pass


class CartOwnershipError(CheckoutServiceError):
    """Raised when user doesn't have permission to access cart/item"""
    pass


class CartValidationError(CheckoutServiceError):
    """Raised when cart validation fails"""
    pass


class CartItemValidationError(CheckoutServiceError):
    """Raised when cart item validation fails"""
    pass
