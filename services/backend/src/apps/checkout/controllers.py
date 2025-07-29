from fastapi import HTTPException, status

from apps.checkout.dto import CartItemResponseDTO, CartResponseDTO
from apps.checkout.interfaces import CartServiceInterface
from apps.checkout.schemas import CartTokenResponse, CartResponse, CartItemResponse, GetCartByTokenRequest
from apps.checkout.exceptions import CartTokenCreationError, CartNotFoundError, CartValidationError
from security.dto import JWTPayloadDTO
from settings.logging_config import get_logger

logger = get_logger(__name__, "checkout")


def _convert_cart_item_dto_to_schema(cart_item_dto: CartItemResponseDTO) -> CartItemResponse:
    """Convert CartItemResponseDTO to CartItemResponse"""
    return CartItemResponse(
        id=cart_item_dto.id,
        product_id=cart_item_dto.product_id,
        product_name=cart_item_dto.product_name,
        product_slug=cart_item_dto.product_slug,
        product_image_url=cart_item_dto.product_image_url,
        quantity=cart_item_dto.quantity,
        unit_price=cart_item_dto.unit_price,
        sale_price=cart_item_dto.sale_price,
        total_price=cart_item_dto.total_price,
        is_available=cart_item_dto.is_available,
        added_at=cart_item_dto.added_at,
    )


def _convert_cart_dto_to_schema(cart_dto: CartResponseDTO) -> CartResponse:
    """Convert CartResponseDTO to CartResponse"""
    cart_items = [_convert_cart_item_dto_to_schema(item) for item in cart_dto.items]

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
        return _convert_cart_dto_to_schema(cart_dto)


async def get_cart_for_user_controller(
        jwt_payload: JWTPayloadDTO,
        cart_service: CartServiceInterface,
) -> CartResponse:
    """
    Controller for getting cart for authenticated user

    Args:
        jwt_payload: JWT payload from verified access token
        cart_service: Service for cart operations

    Returns:
        Cart response with items and totals

    Raises:
        HTTPException: If cart retrieval fails
    """
    logger.info(f"Getting cart for user: {jwt_payload.user_id}")

    try:
        cart_dto = await cart_service.get_or_create_cart_for_user(jwt_payload.user_id)
    except CartValidationError as e:
        logger.error(f"Cart validation error for user {jwt_payload.user_id}: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cart validation error: {e.message}"
        )
    except Exception as e:
        logger.error(f"Unexpected error getting cart for user {jwt_payload.user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
    else:
        return _convert_cart_dto_to_schema(cart_dto)
