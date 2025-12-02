"""FastAPI application entry point."""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.core.config import settings
from app.core.database import init_db, close_db
from app.core.logging import configure_logging, get_logger
from app.core.exceptions import TaskManagementException
from app.api.v1 import api_router

# Configure logging
configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown events."""
    # Startup
    logger.info("Starting Task Management System", version=settings.APP_VERSION)
    await init_db()
    logger.info("Database initialized")
    yield
    # Shutdown
    logger.info("Shutting down Task Management System")
    await close_db()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Enterprise Task Management System with comprehensive features for team collaboration",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(TaskManagementException)
async def task_management_exception_handler(
    request: Request, exc: TaskManagementException
) -> JSONResponse:
    """Handle custom exceptions."""
    logger.warning(
        "Application exception",
        exception=exc.message,
        status_code=exc.status_code,
        details=exc.details,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.message,
            "details": exc.details,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle validation errors."""
    logger.warning("Validation error", errors=exc.errors())
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": exc.errors(),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Handle unexpected exceptions."""
    logger.error("Unexpected error", exception=str(exc), exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An unexpected error occurred",
        },
    )


# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "docs_url": f"{settings.API_V1_PREFIX}/docs",
    }
