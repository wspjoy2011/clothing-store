from fastapi import HTTPException, status

from apps.checkout.interfaces import CartServiceInterface
from apps.checkout.schemas import CartTokenResponse
from apps.checkout.exceptions import CartTokenCreationError
from settings.logging_config import get_logger

logger = get_logger(__name__, "checkout")


async def create_cart_token_controller(
        cart_service: CartServiceInterface,
) -> CartTokenResponse:
    """
    Controller for creating a new cart token for anonymous users

    Args:
        cart_service: Service for cart operations

    Returns:
        Cart token response with token and expiration

    Raises:
        HTTPException: If token creation fails
    """
    logger.info("Creating cart token for anonymous user")

    try:
        cart_token_dto = await cart_service.create_cart_token()
    except CartTokenCreationError as e:
        logger.error(f"Cart token creation failed: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create cart token: {e.message}"
        )
    except Exception as e:
        logger.error(f"Unexpected error creating cart token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
    else:
        return CartTokenResponse(
            token=cart_token_dto.token,
            expires_at=cart_token_dto.expires_at
        )
