"""What the client is told for each cart failure.

The message describes the outcome of the requested action. The cause stays in the
log of the layer that knows it, so a psycopg message written for us cannot reach a
response body.
"""

from apps.checkout.exceptions import (
    CartItemNotFoundError,
    CartItemValidationError,
    CartNotFoundError,
    CartOwnershipError,
    CartStorageError,
    CartTokenCreationError,
    CartValidationError,
    InsufficientStockError,
    ProductNotFoundError,
)

GENERIC_MESSAGE = "The request could not be completed. Please try again."

CLIENT_MESSAGES = {
    CartTokenCreationError: "The cart could not be started. Please try again.",
    CartNotFoundError: "This cart is no longer available.",
    CartItemNotFoundError: "This item is not in your cart.",
    CartOwnershipError: "This item is not in your cart.",
    CartValidationError: "The cart could not be updated with those details.",
    CartItemValidationError: "The item could not be updated with those details.",
    ProductNotFoundError: "This product is no longer available.",
    InsufficientStockError: "There is not enough stock left for that quantity.",
    CartStorageError: "The cart could not be updated right now. Please try again.",
}


def client_message(error: Exception) -> str:
    """
    Get the message the client is allowed to see for a failure

    Args:
        error: Domain exception raised by the service or repository

    Returns:
        Message describing the outcome, never the cause
    """
    for error_type, message in CLIENT_MESSAGES.items():
        if isinstance(error, error_type):
            return message

    return GENERIC_MESSAGE
