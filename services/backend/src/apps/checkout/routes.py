from fastapi import APIRouter, Depends, status, Path, Body

from apps.checkout.controllers import (
    create_cart_token_controller,
    get_cart_by_token_controller,
    get_cart_for_user_controller,
    add_item_to_cart_by_token_controller,
    add_item_to_cart_for_user_controller, remove_cart_item_by_token_controller, remove_cart_item_for_user_controller,
    update_cart_item_for_user_controller, update_cart_item_by_token_controller
)
from apps.checkout.dependencies import get_cart_service
from apps.checkout.interfaces import CartServiceInterface
from apps.checkout.schemas import (
    CartTokenResponse,
    GetCartByTokenRequest,
    CartResponse,
    AddToCartRequest,
    CartItemResponse, UpdateCartItemRequest
)
from security.http import AccessTokenDependency

API_PATHS: dict[str, str] = {
    "create_cart_token": "/cart/token",
    "get_cart_by_token": "/cart/token/get",
    "get_cart": "/cart",
    "add_item_to_cart_by_token": "/cart/token/{token}/items",
    "add_item_to_cart": "/cart/items",
    "remove_cart_item_by_token": "/cart/token/{token}/items/{item_id}",
    "remove_cart_item": "/cart/items/{item_id}",
    "update_cart_item_by_token": "/cart/token/{token}/items/{item_id}",
    "update_cart_item": "/cart/items/{item_id}",
}

router = APIRouter(
    prefix="/checkout",
    tags=["checkout"]
)


@router.post(
    API_PATHS["create_cart_token"],
    response_model=CartTokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create cart token",
    description=(
            "Create a new cart token for anonymous users to store cart items. "
            "This token allows anonymous users to maintain a cart session before login/registration. "
            "The token expires after 30 days and should be included in subsequent cart operations."
    ),
    responses={
        201: {
            "description": "Cart token created successfully",
            "model": CartTokenResponse
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Failed to create cart token: Database connection error"
                    }
                }
            }
        }
    }
)
async def create_cart_token_route(
        cart_service: CartServiceInterface = Depends(get_cart_service)
) -> CartTokenResponse:
    """Create a new cart token for anonymous users.

    This endpoint generates a unique token that anonymous users can use
    to store items in their cart before registration or login.

    Args:
        cart_service: Cart service dependency for business logic operations.

    Returns:
        CartTokenResponse: Cart token with expiration date.

    Note:
        - Token validity: 30 days from creation
        - Usage: Store the token and send it with subsequent cart operations
        - Required for anonymous cart functionality
    """
    return await create_cart_token_controller(cart_service)


@router.post(
    API_PATHS["get_cart_by_token"],
    response_model=CartResponse,
    status_code=status.HTTP_200_OK,
    summary="Get cart by token",
    description=(
            "Get or create cart for anonymous user by token. "
            "If cart doesn't exist for the token, a new empty cart will be created. "
            "Returns complete cart information including items, totals, and availability status."
    ),
    responses={
        200: {
            "description": "Cart retrieved successfully",
            "model": CartResponse
        },
        400: {
            "description": "Cart validation error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Cart validation error: Invalid cart state"
                    }
                }
            }
        },
        404: {
            "description": "Cart token not found or expired",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Cart not found: Cart token not found or expired"
                    }
                }
            }
        },
        422: {
            "description": "Request validation error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Token must be a non-empty string"
                    }
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Internal server error"
                    }
                }
            }
        }
    }
)
async def get_cart_by_token_route(
        request_data: GetCartByTokenRequest,
        cart_service: CartServiceInterface = Depends(get_cart_service)
) -> CartResponse:
    """Get or create cart for anonymous user by token.

    This endpoint retrieves an existing cart for the provided token or creates
    a new empty cart if one doesn't exist. The token must be valid and not expired.

    Args:
        request_data: Request data containing the cart token.
        cart_service: Cart service dependency for business logic operations.

    Returns:
        CartResponse: Complete cart information with items and totals.

    Note:
        - Creates new cart if token is valid but cart doesn't exist
        - Returns 404 if token is invalid or expired
        - All cart items include availability status and pricing
    """
    return await get_cart_by_token_controller(request_data, cart_service)


@router.get(
    API_PATHS["get_cart"],
    response_model=CartResponse,
    status_code=status.HTTP_200_OK,
    summary="Get cart for authenticated user",
    description=(
            "Get or create cart for authenticated user. "
            "If cart doesn't exist for the user, a new empty cart will be created. "
            "Returns complete cart information including items, totals, and availability status."
    ),
    responses={
        200: {
            "description": "Cart retrieved successfully",
            "model": CartResponse
        },
        400: {
            "description": "Cart validation error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Cart validation error: Invalid cart state"
                    }
                }
            }
        },
        401: {
            "description": "Authentication required",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Authorization header is missing"
                    }
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Internal server error"
                    }
                }
            }
        }
    }
)
async def get_cart_route(
        jwt_payload: AccessTokenDependency,
        cart_service: CartServiceInterface = Depends(get_cart_service)
) -> CartResponse:
    """Get or create cart for authenticated user.

    This endpoint retrieves an existing cart for the authenticated user or creates
    a new empty cart if one doesn't exist. Authentication is required via Bearer token.

    Args:
        jwt_payload: JWT payload from verified access token.
        cart_service: Cart service dependency for business logic operations.

    Returns:
        CartResponse: Complete cart information with items and totals.

    Note:
        - Requires valid Bearer token in Authorization header
        - Creates new cart if user doesn't have one yet
        - All cart items include availability status and pricing
        - User-specific cart, isolated from anonymous carts
    """
    return await get_cart_for_user_controller(jwt_payload, cart_service)


@router.post(
    API_PATHS["add_item_to_cart_by_token"],
    response_model=CartItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add item to cart by token",
    description=(
            "Add item to cart for anonymous user using cart token. "
            "Validates product availability and stock before adding. "
            "If item already exists in cart, quantity will be updated."
    ),
    responses={
        201: {
            "description": "Item added to cart successfully",
            "model": CartItemResponse
        },
        400: {
            "description": "Insufficient stock or validation error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Insufficient stock for product 123"
                    }
                }
            }
        },
        404: {
            "description": "Cart token or product not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Product with ID 123 not found"
                    }
                }
            }
        },
        422: {
            "description": "Request validation error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Quantity must be between 1 and 999"
                    }
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Internal server error"
                    }
                }
            }
        }
    }
)
async def add_item_to_cart_by_token_route(
        token: str = Path(..., description="Cart token for anonymous user"),
        request_data: AddToCartRequest = Body(...),
        cart_service: CartServiceInterface = Depends(get_cart_service)
) -> CartItemResponse:
    """Add item to cart for anonymous user by token.

    This endpoint adds a product to the cart associated with the provided token.
    It validates product existence, availability, and stock before adding.

    Args:
        token: Cart token for anonymous user.
        request_data: Request data containing product ID and quantity.
        cart_service: Cart service dependency for business logic operations.

    Returns:
        CartItemResponse: Added cart item with product details and pricing.

    Note:
        - Validates product existence and availability
        - Checks stock availability before adding
        - Updates quantity if item already exists in cart
        - Returns complete product information with current pricing
    """
    return await add_item_to_cart_by_token_controller(token, request_data, cart_service)


@router.post(
    API_PATHS["add_item_to_cart"],
    response_model=CartItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add item to user cart",
    description=(
            "Add item to cart for authenticated user. "
            "Validates product availability and stock before adding. "
            "If item already exists in cart, quantity will be updated."
    ),
    responses={
        201: {
            "description": "Item added to cart successfully",
            "model": CartItemResponse
        },
        400: {
            "description": "Insufficient stock or validation error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Insufficient stock for product 123"
                    }
                }
            }
        },
        401: {
            "description": "Authentication required",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Authorization header is missing"
                    }
                }
            }
        },
        404: {
            "description": "Product not found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Product with ID 123 not found"
                    }
                }
            }
        },
        422: {
            "description": "Request validation error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Quantity must be between 1 and 999"
                    }
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Internal server error"
                    }
                }
            }
        }
    }
)
async def add_item_to_cart_route(
        jwt_payload: AccessTokenDependency,
        request_data: AddToCartRequest = Body(...),
        cart_service: CartServiceInterface = Depends(get_cart_service)
) -> CartItemResponse:
    """Add item to cart for authenticated user.

    This endpoint adds a product to the cart for the authenticated user.
    It validates product existence, availability, and stock before adding.

    Args:
        request_data: Request data containing product ID and quantity.
        jwt_payload: JWT payload from verified access token.
        cart_service: Cart service dependency for business logic operations.

    Returns:
        CartItemResponse: Added cart item with product details and pricing.

    Note:
        - Requires valid Bearer token in Authorization header
        - Validates product existence and availability
        - Checks stock availability before adding
        - Updates quantity if item already exists in cart
        - Returns complete product information with current pricing
    """
    return await add_item_to_cart_for_user_controller(request_data, jwt_payload, cart_service)


@router.delete(
    API_PATHS["remove_cart_item_by_token"],
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove item from cart by token",
    description=(
            "Remove item from cart for anonymous user using cart token. "
            "Validates ownership - item must belong to the cart associated with the provided token."
    ),
    responses={
        204: {
            "description": "Item removed successfully"
        },
        404: {
            "description": "Cart token not found, expired, or item not found in cart",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Cart token not found or expired"
                    }
                }
            }
        },
        422: {
            "description": "Request validation error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Item ID must be a positive integer"
                    }
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Internal server error"
                    }
                }
            }
        }
    }
)
async def remove_cart_item_by_token_route(
        token: str = Path(..., description="Cart token for anonymous user"),
        item_id: int = Path(..., gt=0, description="ID of the cart item to remove"),
        cart_service: CartServiceInterface = Depends(get_cart_service)
):
    """Remove item from cart for anonymous user by token.

    This endpoint removes a specific item from the cart associated with the provided token.
    The item must belong to the cart to be removed (ownership validation).

    Args:
        token: Cart token for anonymous user.
        item_id: ID of the cart item to remove.
        cart_service: Cart service dependency for business logic operations.

    Returns:
        HTTP 204 No Content on successful removal.

    Note:
        - Validates token existence and expiration
        - Validates item ownership (item must belong to the token's cart)
        - Returns 404 if token is invalid or item doesn't belong to cart
        - Idempotent operation - returns 204 even if item was already removed
    """
    return await remove_cart_item_by_token_controller(token, item_id, cart_service)


@router.delete(
    API_PATHS["remove_cart_item"],
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove item from user cart",
    description=(
            "Remove item from cart for authenticated user. "
            "Validates ownership - item must belong to the user's cart."
    ),
    responses={
        204: {
            "description": "Item removed successfully"
        },
        401: {
            "description": "Authentication required",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Authorization header is missing"
                    }
                }
            }
        },
        404: {
            "description": "Item not found in user's cart",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Cart item not found in your cart"
                    }
                }
            }
        },
        422: {
            "description": "Request validation error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Item ID must be a positive integer"
                    }
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Internal server error"
                    }
                }
            }
        }
    }
)
async def remove_cart_item_route(
        jwt_payload: AccessTokenDependency,
        item_id: int = Path(..., gt=0, description="ID of the cart item to remove"),
        cart_service: CartServiceInterface = Depends(get_cart_service)
):
    """Remove item from cart for authenticated user.

    This endpoint removes a specific item from the authenticated user's cart.
    The item must belong to the user's cart to be removed (ownership validation).

    Args:
        item_id: ID of the cart item to remove.
        jwt_payload: JWT payload from verified access token.
        cart_service: Cart service dependency for business logic operations.

    Returns:
        HTTP 204 No Content on successful removal.

    Note:
        - Requires valid Bearer token in Authorization header
        - Validates item ownership (item must belong to user's cart)
        - Returns 404 if item doesn't belong to user's cart
        - Idempotent operation - returns 204 even if item was already removed
    """
    return await remove_cart_item_for_user_controller(item_id, jwt_payload, cart_service)


@router.put(
    API_PATHS["update_cart_item_by_token"],
    response_model=CartItemResponse,
    status_code=status.HTTP_200_OK,
    summary="Update item quantity by token",
    description=(
        "Update quantity of a cart item for an anonymous user using a cart token. "
        "Validates that the item belongs to the token's cart."
    ),
    responses={
        200: {
            "description": "Cart item updated successfully",
            "model": CartItemResponse
        },
        404: {
            "description": "Cart token not found/expired or item not found in token's cart",
            "content": {
                "application/json": {
                    "example": {"detail": "Cart item not found in this cart"}
                }
            }
        },
        422: {
            "description": "Request validation error",
            "content": {
                "application/json": {
                    "example": {"detail": "Quantity must be between 1 and 999"}
                }
            }
        },
        500: {"description": "Internal server error"}
    }
)
async def update_cart_item_by_token_route(
    token: str = Path(..., description="Cart token for anonymous user"),
    item_id: int = Path(..., gt=0, description="ID of the cart item to update"),
    request_data: UpdateCartItemRequest = Body(...),
    cart_service: CartServiceInterface = Depends(get_cart_service)
) -> CartItemResponse:
    """
    Update cart item quantity for anonymous carts identified by token.
    """
    return await update_cart_item_by_token_controller(token, item_id, request_data, cart_service)


@router.put(
    API_PATHS["update_cart_item"],
    response_model=CartItemResponse,
    status_code=status.HTTP_200_OK,
    summary="Update item quantity in user cart",
    description=(
        "Update quantity of a cart item for an authenticated user. "
        "Validates that the item belongs to the user's cart."
    ),
    responses={
        200: {
            "description": "Cart item updated successfully",
            "model": CartItemResponse
        },
        401: {
            "description": "Authentication required",
            "content": {
                "application/json": {
                    "example": {"detail": "Authorization header is missing"}
                }
            }
        },
        404: {
            "description": "Cart item not found in user's cart",
            "content": {
                "application/json": {
                    "example": {"detail": "Cart item not found in your cart"}
                }
            }
        },
        422: {
            "description": "Request validation error",
            "content": {
                "application/json": {
                    "example": {"detail": "Quantity must be between 1 and 999"}
                }
            }
        },
        500: {"description": "Internal server error"}
    }
)
async def update_cart_item_route(
    jwt_payload: AccessTokenDependency,
    item_id: int = Path(..., gt=0, description="ID of the cart item to update"),
    request_data: UpdateCartItemRequest = Body(...),
    cart_service: CartServiceInterface = Depends(get_cart_service)
) -> CartItemResponse:
    """
    Update cart item quantity for authenticated users.
    """
    return await update_cart_item_for_user_controller(jwt_payload, item_id, request_data, cart_service)
