"""
Utility functions for handling exceptions in API routes.
"""
import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import BaseModel, Field
from typing import List, Optional

from app.models.exceptions import GameError

logger = logging.getLogger(__name__)


class ErrorResponse(BaseModel):
    """Standard model for API error responses."""
    detail: str
    errors: Optional[List[str]] = Field(None, description="A list of specific validation errors.")


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions globally with a consistent format."""
    logger.warning(f"HTTP exception: {exc.detail} (status_code={exc.status_code})")
    error_content = ErrorResponse(detail=exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content=error_content.model_dump(exclude_none=True)
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors with a user-friendly format."""
    errors = []
    for error in exc.errors():
        location = ".".join(map(str, error.get("loc", [])))
        errors.append(f"Field '{location}': {error.get('msg')}")
            
    logger.warning(f"Validation error: {errors}")
    error_content = ErrorResponse(detail="Validation error", errors=errors)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_content.model_dump(exclude_none=True)
    )


async def game_exception_handler(request: Request, exc: GameError):
    """Handle game-specific exceptions."""
    logger.warning(f"Game error: {exc.detail} (status_code={exc.status_code})")
    error_content = ErrorResponse(detail=exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content=error_content.model_dump(exclude_none=True)
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """Catch-all for any unhandled exceptions to prevent exposing stack traces."""
    logger.exception(f"Unhandled exception: {str(exc)}")
    error_content = ErrorResponse(detail="An internal server error occurred")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_content.model_dump(exclude_none=True)
    )


def register_exception_handlers(app: FastAPI):
    """Register all exception handlers for the application."""
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(GameError, game_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)