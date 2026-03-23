from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse


class RiftError(Exception):
    """Base class for all application errors."""

    status_code: int = 500
    error_code: str = "INTERNAL_ERROR"

    def __init__(self, message: str, details: dict | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class NotFoundError(RiftError):
    status_code = 404
    error_code = "NOT_FOUND"


class ConflictError(RiftError):
    status_code = 409
    error_code = "CONFLICT"


class ValidationError(RiftError):
    status_code = 422
    error_code = "VALIDATION_ERROR"


class AuthenticationError(RiftError):
    status_code = 401
    error_code = "AUTHENTICATION_REQUIRED"


class AuthorizationError(RiftError):
    status_code = 403
    error_code = "FORBIDDEN"


class OptimisticLockError(RiftError):
    status_code = 409
    error_code = "OPTIMISTIC_LOCK_CONFLICT"

    def __init__(self, resource: str, expected_version: int) -> None:
        super().__init__(
            f"Optimistic lock conflict on {resource}: expected version {expected_version}"
        )


class StateTransitionError(RiftError):
    status_code = 422
    error_code = "INVALID_STATE_TRANSITION"

    def __init__(self, resource: str, from_state: str, to_state: str) -> None:
        super().__init__(
            f"Invalid state transition on {resource}: {from_state} -> {to_state}"
        )


async def rift_error_handler(request: Request, exc: RiftError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred.",
                "details": {},
            }
        },
    )
