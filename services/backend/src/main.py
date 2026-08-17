from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from apps.accounts.routes.accounts import router as accounts_router
from apps.accounts.routes.social_auth import router as auth_router
from apps.catalog.routes import router as catalog_router
from apps.checkout.routes import router as checkout_router
from search.dependencies import cleanup_autocomplete_client
from security.rate_limit import limiter, rate_limit_exceeded_handler
from settings.api import API_VERSION_PREFIX
from settings.config import config
from settings.logging_config import get_logger

logger = get_logger(__name__, "main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info("Application startup: initializing resources...")
    yield
    # Shutdown
    logger.info("Application shutdown: cleaning up resources...")
    await cleanup_autocomplete_client()
    logger.info("Application shutdown complete")


app = FastAPI(
    title="Clothing Store Backend API",
    description="This API serves as the backend for an online clothing store, providing endpoints "
                "for managing products, categories, and user interactions.",
    lifespan=lifespan
)


app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)


app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    error = exc.errors()[0]
    return JSONResponse(
        status_code=422,
        content={
            "field": error["loc"][-1],
            "message": error["msg"]
        },
    )


app.include_router(catalog_router, prefix=f"{API_VERSION_PREFIX}")
app.include_router(accounts_router, prefix=f"{API_VERSION_PREFIX}")
app.include_router(auth_router, prefix=f"{API_VERSION_PREFIX}")
app.include_router(checkout_router, prefix=f"{API_VERSION_PREFIX}")
