"""
Utility functions for handling exceptions in API routes.
"""
import logging
import functools
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.models.exceptions import GameError

logger = logging.getLogger(__name__)


def handle_exceptions(func):
    """
    Decorator for handling exceptions in route handlers.
    
    This decorator:
    1. Catches all exceptions
    2. Re-raises HTTPException and GameError (which extends HTTPException)
    3. Logs unexpected exceptions
    4. Returns a consistent error response for unexpected exceptions
    
    Usage:
        @router.get("/endpoint")
        @handle_exceptions
        async def my_endpoint():
            # Your code here
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except (HTTPException, GameError):
            # Re-raise HTTP exceptions and GameError to maintain their status codes
            raise
        except Exception as e:
            # Log the exception
            logger.exception(f"Unhandled error in {func.__name__}: {str(e)}")
            
            # Return a consistent error response without exposing implementation details
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "An internal server error occurred"}
            )
    return wrapper


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions globally with consistent format"""
    logger.warning(f"HTTP exception: {exc.detail} (status_code={exc.status_code})")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with user-friendly format"""
    errors = []
    for error in exc.errors():
        location = error.get("loc", [])
        if len(location) > 0 and location[0] == "body":
            field = ".".join([str(loc) for loc in location[1:]])
            errors.append(f"Field '{field}': {error.get('msg')}")
        else:
            errors.append(error.get("msg"))
            
    logger.warning(f"Validation error: {errors}")
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation error", "errors": errors}
    )


async def game_exception_handler(request: Request, exc: GameError):
    """Handle game-specific exceptions"""
    logger.warning(f"Game error: {exc.detail} (status_code={exc.status_code})")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """Catch-all for any unhandled exceptions to prevent 500 errors with stack traces"""
    logger.exception(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred"}
    )


def register_exception_handlers(app: FastAPI):
    """Register all exception handlers to an application"""
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(GameError, game_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
