from typing import Annotated

from fastapi import Request, HTTPException, status, Depends

from security.dependencies import get_jwt_manager
from security.dto import JWTPayloadDTO
from security.interfaces import JWTManagerInterface
from security.exceptions import (
    EmptyTokenError,
    ExpiredTokenError,
    InvalidTokenError,
    TokenSignatureError,
    InvalidTokenTypeError,
    TokenVerificationError
)


def get_token(request: Request) -> str:
    """
    Extracts the Bearer token from the Authorization header.

    :param request: FastAPI Request object.
    :return: Extracted token string.
    :raises HTTPException: If Authorization header is missing or invalid.
    """
    authorization: str = request.headers.get("Authorization")

    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is missing"
        )

    scheme, _, token = authorization.partition(" ")

    if scheme.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format. Expected 'Bearer <token>'"
        )

    return token


def get_verified_access_token(
        token: str = Depends(get_token),
        jwt_manager: JWTManagerInterface = Depends(get_jwt_manager)
) -> JWTPayloadDTO:
    """
    Verify access token and return payload.

    :param token: JWT token from Authorization header
    :param jwt_manager: JWT manager instance
    :return: Verified JWT payload
    :raises HTTPException: If token is invalid, expired, or verification fails
    """
    try:
        payload = jwt_manager.verify_access_token(token)
        return JWTPayloadDTO.from_payload(payload)
    except EmptyTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is empty"
        )
    except ExpiredTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format"
        )
    except TokenSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token signature"
        )
    except InvalidTokenTypeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )
    except TokenVerificationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token verification failed: {str(e)}"
        )


JWTTokenDependency = Annotated[str, Depends(get_token)]
AccessTokenDependency = Annotated[JWTPayloadDTO, Depends(get_verified_access_token)]
