"""
CoroVista Backend - Standard Error Definitions & Exception Handlers
Stage 4: FastAPI Backend + Prediction/Explainability API
"""

from typing import Any, List, Optional
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field


class ErrorDetails(BaseModel):
    code: str = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error description")
    details: List[Any] = Field(default_factory=list, description="Context-specific error details")


class ErrorEnvelope(BaseModel):
    error: ErrorDetails


class CoroVistaAPIException(Exception):
    """Base API exception with HTTP status code and standardized error envelope."""

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Optional[List[Any]] = None,
    ):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or []


HTTP_422 = getattr(status, "HTTP_422_UNPROCESSABLE_CONTENT", 422)


class InvalidInputError(CoroVistaAPIException):
    """Raised when patient input fails clinical validation or contains leaked targets."""

    def __init__(self, message: str, details: Optional[List[Any]] = None):
        super().__init__(
            code="INVALID_INPUT",
            message=message,
            status_code=HTTP_422,
            details=details,
        )


class InvalidTargetError(CoroVistaAPIException):
    """Raised when an unrecognized target is requested for explanation."""

    def __init__(self, target: str):
        super().__init__(
            code="INVALID_TARGET",
            message=f"Target '{target}' is not a valid prediction target. Must be one of: 'cath', 'lad', 'lcx', 'rca'.",
            status_code=status.HTTP_400_BAD_REQUEST,
            details=[{"target": target, "valid_targets": ["cath", "lad", "lcx", "rca"]}],
        )


class ModelUnavailableError(CoroVistaAPIException):
    """Raised when serialized model artifacts cannot be loaded from disk."""

    def __init__(self, message: str = "Required model artifacts are unavailable or failed to initialize."):
        super().__init__(
            code="SERVICE_UNAVAILABLE",
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=[],
        )


async def corovista_exception_handler(request: Request, exc: CoroVistaAPIException) -> JSONResponse:
    """Handles all domain CoroVistaAPIException instances."""
    envelope = ErrorEnvelope(
        error=ErrorDetails(
            code=exc.code,
            message=exc.message,
            details=exc.details,
        )
    )
    return JSONResponse(status_code=exc.status_code, content=envelope.model_dump())


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Normalizes FastAPI/Pydantic validation errors into standard error schema."""
    cleaned_details = []
    for err in exc.errors():
        cleaned_details.append({
            "loc": err.get("loc"),
            "msg": err.get("msg"),
            "type": err.get("type"),
        })

    envelope = ErrorEnvelope(
        error=ErrorDetails(
            code="INVALID_INPUT",
            message="Request input validation failed. Please check the provided fields and data types.",
            details=cleaned_details,
        )
    )
    return JSONResponse(status_code=HTTP_422, content=envelope.model_dump())


async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    """Translates Python ValueErrors from inference/validation into standard 422 error."""
    msg = str(exc)
    code = "INVALID_INPUT"
    status_code = HTTP_422

    if "Unknown target" in msg:
        code = "INVALID_TARGET"
        status_code = status.HTTP_400_BAD_REQUEST

    envelope = ErrorEnvelope(
        error=ErrorDetails(
            code=code,
            message=msg,
            details=[],
        )
    )
    return JSONResponse(status_code=status_code, content=envelope.model_dump())


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catches unhandled errors without leaking stack traces or internal filepaths."""
    envelope = ErrorEnvelope(
        error=ErrorDetails(
            code="INTERNAL_ERROR",
            message="An unexpected internal server error occurred while processing the request.",
            details=[],
        )
    )
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=envelope.model_dump())
