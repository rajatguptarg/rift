from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse

from src.core import logging as log_module
from src.core.errors import AuthenticationError

logger = log_module.get_logger(__name__)


async def auth_middleware(request: Request, call_next):  # type: ignore[no-untyped-def]
    """
    JWT / token validation middleware.
    Public paths (/health, /docs, /openapi.json, /webhooks) bypass auth.
    """
    public_prefixes = ("/health", "/docs", "/openapi.json", "/redoc", "/webhooks")

    if any(request.url.path.startswith(p) for p in public_prefixes):
        return await call_next(request)

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return JSONResponse(
            status_code=401,
            content={"error": {"code": "AUTHENTICATION_REQUIRED", "message": "Missing or invalid Authorization header.", "details": {}}},
        )

    token = auth_header.removeprefix("Bearer ").strip()

    from src.core.config import settings
    from jose import JWTError, jwt as jose_jwt

    try:
        payload = jose_jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError:
        return JSONResponse(
            status_code=401,
            content={"error": {"code": "AUTHENTICATION_REQUIRED", "message": "Invalid or expired token.", "details": {}}},
        )

    # Attach decoded claims to request state for downstream use
    request.state.user_id = payload.get("sub")
    request.state.email = payload.get("email", "")
    request.state.scopes = payload.get("scopes", [])

    # Set correlation ID from token subject for tracing
    log_module.set_correlation_id(payload.get("jti", log_module.get_correlation_id()))

    return await call_next(request)
