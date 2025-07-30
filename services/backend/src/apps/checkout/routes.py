from fastapi import APIRouter, Depends, status

from apps.checkout.controllers import create_cart_token_controller, get_cart_by_token_controller, \
    get_cart_for_user_controller
from apps.checkout.dependencies import get_cart_service
from apps.checkout.interfaces import CartServiceInterface
from apps.checkout.schemas import CartTokenResponse, GetCartByTokenRequest, CartResponse
from security.http import AccessTokenDependency

API_PATHS: dict[str, str] = {
    "create_cart_token": "/cart/token",
    "get_cart_by_token": "/cart/token/get",
    "get_cart": "/cart",
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
