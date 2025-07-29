from fastapi import APIRouter, Depends, status

from apps.checkout.controllers import create_cart_token_controller
from apps.checkout.dependencies import get_cart_service
from apps.checkout.interfaces import CartServiceInterface
from apps.checkout.schemas import CartTokenResponse

API_PATHS: dict[str, str] = {
    "create_cart_token": "/cart/token",
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
