from fastapi import HTTPException, status

from apps.checkout.interfaces import CartServiceInterface
from apps.checkout.schemas import CartTokenResponse, CartResponse, CartItemResponse, GetCartByTokenRequest
from apps.checkout.exceptions import CartTokenCreationError, CartNotFoundError, CartValidationError
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


async def get_cart_by_token_controller(
        request_data: GetCartByTokenRequest,
        cart_service: CartServiceInterface,
) -> CartResponse:
    """
    Controller for getting cart by token

    Args:
        request_data: Request data with cart token
        cart_service: Service for cart operations

    Returns:
        Cart response with items and totals

    Raises:
        HTTPException: If cart retrieval fails
    """
    logger.info(f"Getting cart for token: {request_data.token[:10]}...")

    try:
        cart_dto = await cart_service.get_or_create_cart_for_token(request_data.token)
    except CartNotFoundError as e:
        logger.warning(f"Cart not found for token {request_data.token[:10]}...: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cart not found: {e.message}"
        )
    except CartValidationError as e:
        logger.error(f"Cart validation error for token {request_data.token[:10]}...: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cart validation error: {e.message}"
        )
    except Exception as e:
        logger.error(f"Unexpected error getting cart for token {request_data.token[:10]}...: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
    else:
        cart_items = [
            CartItemResponse(
                id=item.id,
                product_id=item.product_id,
                product_name=item.product_name,
                product_slug=item.product_slug,
                product_image_url=item.product_image_url,
                quantity=item.quantity,
                unit_price=item.unit_price,
                sale_price=item.sale_price,
                total_price=item.total_price,
                is_available=item.is_available,
                added_at=item.added_at,
            )
            for item in cart_dto.items
        ]

        return CartResponse(
            id=cart_dto.id,
            items=cart_items,
            total_items=cart_dto.total_items,
            total_amount=cart_dto.total_amount,
            total_discount=cart_dto.total_discount,
            final_amount=cart_dto.final_amount,
            created_at=cart_dto.created_at,
            updated_at=cart_dto.updated_at,
        )
