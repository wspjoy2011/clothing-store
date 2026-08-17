from fastapi import HTTPException, status, Response

from apps.checkout.dto import CartItemResponseDTO, CartResponseDTO, AddToCartRequestDTO, UpdateCartItemRequestDTO
from apps.checkout.interfaces import CartServiceInterface
from apps.checkout.schemas import CartTokenResponse, CartResponse, CartItemResponse, GetCartByTokenRequest, \
    AddToCartRequest, UpdateCartItemRequest
from apps.checkout.exceptions import CartStorageError, CartTokenCreationError, CartNotFoundError, CartValidationError, \
    ProductNotFoundError, InsufficientStockError
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


def _convert_add_to_cart_request_to_dto(request: AddToCartRequest) -> AddToCartRequestDTO:
    """Convert AddToCartRequest to AddToCartRequestDTO"""
    return AddToCartRequestDTO(
        product_id=request.product_id,
        quantity=request.quantity
    )


def _convert_update_item_request_to_dto(request: UpdateCartItemRequest, item_id: int) -> UpdateCartItemRequestDTO:
    """Convert UpdateCartItemRequest + path item_id to UpdateCartItemRequestDTO"""
    return UpdateCartItemRequestDTO(
        cart_item_id=item_id,
        quantity=request.quantity
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


async def add_item_to_cart_by_token_controller(
        token: str,
        request_data: AddToCartRequest,
        cart_service: CartServiceInterface,
) -> CartItemResponse:
    """
    Controller for adding item to cart by token (anonymous user)

    Args:
        token: Cart token for anonymous user
        request_data: Request data for adding item to cart
        cart_service: Service for cart operations

    Returns:
        Added cart item response

    Raises:
        HTTPException: If adding item fails
    """
    logger.info(f"Adding item to cart by token: {token[:10]}..., product_id={request_data.product_id}")

    try:
        request_dto = _convert_add_to_cart_request_to_dto(request_data)
        cart_item_dto = await cart_service.add_item_to_cart(request_dto, token=token)
    except CartNotFoundError as e:
        logger.warning(f"Cart not found for token {token[:10]}...: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cart not found: {e.message}"
        )
    except ProductNotFoundError as e:
        logger.warning(f"Product not found: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product not found: {e.message}"
        )
    except InsufficientStockError as e:
        logger.warning(f"Insufficient stock: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient stock: {e.message}"
        )
    except Exception as e:
        logger.error(f"Unexpected error adding item to cart by token {token[:10]}...: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
    else:
        return _convert_cart_item_dto_to_schema(cart_item_dto)


async def add_item_to_cart_for_user_controller(
        request_data: AddToCartRequest,
        jwt_payload: JWTPayloadDTO,
        cart_service: CartServiceInterface,
) -> CartItemResponse:
    """
    Controller for adding item to cart for authenticated user

    Args:
        request_data: Request data for adding item to cart
        jwt_payload: JWT payload from verified access token
        cart_service: Service for cart operations

    Returns:
        Added cart item response

    Raises:
        HTTPException: If adding item fails
    """
    logger.info(f"Adding item to cart for user {jwt_payload.user_id}, product_id={request_data.product_id}")

    try:
        request_dto = _convert_add_to_cart_request_to_dto(request_data)
        cart_item_dto = await cart_service.add_item_to_cart(request_dto, user_id=jwt_payload.user_id)
    except ProductNotFoundError as e:
        logger.warning(f"Product not found: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product not found: {e.message}"
        )
    except InsufficientStockError as e:
        logger.warning(f"Insufficient stock: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient stock: {e.message}"
        )
    except CartValidationError as e:
        logger.error(f"Cart validation error for user {jwt_payload.user_id}: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cart validation error: {e.message}"
        )
    except Exception as e:
        logger.error(f"Unexpected error adding item to cart for user {jwt_payload.user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
    else:
        return _convert_cart_item_dto_to_schema(cart_item_dto)


async def remove_cart_item_by_token_controller(
        token: str,
        item_id: int,
        cart_service: CartServiceInterface
):
    """
    Controller for removing cart item by token

    Args:
        token: Cart token for anonymous user
        item_id: ID of the cart item to remove
        cart_service: Cart service for business logic

    Returns:
        HTTP 204 No Content on success

    Raises:
        HTTPException: Various HTTP errors based on business logic results
    """
    try:
        success = await cart_service.remove_cart_item(
            item_id=item_id,
            token=token
        )
    except CartNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except CartStorageError as e:
        logger.error(f"Cart item {item_id} could not be removed: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The item could not be removed right now. Please try again."
        )
    except Exception as e:
        logger.error(f"Unexpected error removing cart item {item_id} by token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
    else:
        if success:
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cart item with ID {item_id} not found in cart"
            )


async def remove_cart_item_for_user_controller(
        item_id: int,
        jwt_payload: JWTPayloadDTO,
        cart_service: CartServiceInterface
):
    """
    Controller for removing cart item for authenticated user

    Args:
        item_id: ID of the cart item to remove
        jwt_payload: JWT payload with user information
        cart_service: Cart service for business logic

    Returns:
        HTTP 204 No Content on success

    Raises:
        HTTPException: Various HTTP errors based on business logic results
    """
    try:
        success = await cart_service.remove_cart_item(
            item_id=item_id,
            user_id=jwt_payload.user_id
        )
    except CartNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except CartStorageError as e:
        logger.error(f"Cart item {item_id} could not be removed: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The item could not be removed right now. Please try again."
        )
    except Exception as e:
        logger.error(f"Unexpected error removing cart item {item_id} for user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
    else:
        if success:
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cart item with ID {item_id} not found in cart"
            )


async def update_cart_item_by_token_controller(
        token: str,
        item_id: int,
        request_data: UpdateCartItemRequest,
        cart_service: CartServiceInterface,
) -> CartItemResponse:
    """
    Controller for updating cart item quantity by token (anonymous user)
    """
    logger.info(f"Updating cart item by token: {token[:10]}..., item_id={item_id}, quantity={request_data.quantity}")

    request_dto = _convert_update_item_request_to_dto(request_data, item_id)

    try:
        updated_item_dto = await cart_service.update_cart_item(request_dto, token=token)
    except CartNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ProductNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except InsufficientStockError as e:
        logger.warning(f"Insufficient stock: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient stock: {e.message}"
        )
    except Exception as e:
        logger.error(f"Unexpected error updating cart item {item_id} by token {token[:10]}...: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
    else:
        return _convert_cart_item_dto_to_schema(updated_item_dto)


async def update_cart_item_for_user_controller(
        item_id: int,
        jwt_payload: JWTPayloadDTO,
        request_data: UpdateCartItemRequest,
        cart_service: CartServiceInterface,
) -> CartItemResponse:
    """
    Controller for updating cart item quantity for authenticated user
    """
    logger.info(
        f"Updating cart item for user {jwt_payload.user_id}: item_id={item_id}, quantity={request_data.quantity}")

    request_dto = _convert_update_item_request_to_dto(request_data, item_id)

    try:
        updated_item_dto = await cart_service.update_cart_item(request_dto, user_id=jwt_payload.user_id)
    except CartNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ProductNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except InsufficientStockError as e:
        logger.warning(f"Insufficient stock: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient stock: {e.message}"
        )
    except Exception as e:
        logger.error(f"Unexpected error updating cart item {item_id} for user {jwt_payload.user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
    else:
        return _convert_cart_item_dto_to_schema(updated_item_dto)
