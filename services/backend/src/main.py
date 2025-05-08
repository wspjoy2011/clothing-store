from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from apps.catalog.routes import router as catalog_router

app = FastAPI(
    title="Clothing Store Backend API",
    description="This API serves as the backend for an online clothing store, providing endpoints "
                "for managing products, categories, and user interactions."
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
