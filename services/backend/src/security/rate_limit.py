from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from settings.config import config
from settings.logging_config import get_logger

logger = get_logger(__name__, "security")

limiter = Limiter(key_func=get_remote_address)

# Limits
CREDENTIAL_GUESS_LIMIT = config.RATE_LIMIT_CREDENTIAL_GUESS
REGISTRATION_LIMIT = config.RATE_LIMIT_REGISTRATION
EMAIL_DISPATCH_LIMIT = config.RATE_LIMIT_EMAIL_DISPATCH

RETRY_MESSAGE = "Too many attempts. Please wait a minute and try again."


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """
    Answer a caller that exceeded the limit for an endpoint

    The response states what to do next and nothing about the limit itself: the
    configured rate is useful to us in the log, not to whoever is probing it.

    Args:
        request: Request that crossed the limit
        exc: Limit that was exceeded

    Returns:
        A 429 response asking the caller to retry later
    """
    logger.warning(
        f"Rate limit {exc.detail} reached on {request.method} {request.url.path} "
        f"by {get_remote_address(request)}"
    )

    return JSONResponse(
        status_code=429,
        content={"detail": RETRY_MESSAGE}
    )
