from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from settings.config import config
from settings.logging_config import get_logger
from apps.catalog.routes import router as catalog_router
from search.dependencies import cleanup_autocomplete_client

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


API_VERSION_PREFIX = "/api/v1"

app.include_router(catalog_router, prefix=f"{API_VERSION_PREFIX}")
