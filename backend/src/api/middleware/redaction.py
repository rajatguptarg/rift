from __future__ import annotations

from fastapi import Request

from src.core.logging import get_logger

logger = get_logger(__name__)


async def redaction_middleware(request: Request, call_next):  # type: ignore[no-untyped-def]
    """
    Repository access redaction middleware.
    After the response is built, this middleware can redact sensitive fields
    based on the user's namespace visibility policy.

    For now this is a passthrough — actual per-response redaction is applied
    at the service layer using the AuthorizationContext injected via DI.
    """
    response = await call_next(request)
    return response
