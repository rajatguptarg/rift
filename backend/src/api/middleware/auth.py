from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse

from src.core import logging as log_module

logger = log_module.get_logger(__name__)

_PUBLIC_PREFIXES = (
    "/health",
    "/docs",
    "/openapi.json",
    "/redoc",
    "/webhooks",
    "/api/v1/auth/sign-in",
    "/api/v1/auth/sign-up",
)


async def auth_middleware(request: Request, call_next):  # type: ignore[no-untyped-def]
    """
    JWT / token validation middleware.
    Public paths bypass auth; all others require a valid Bearer token.
    """
    if any(request.url.path.startswith(p) for p in _PUBLIC_PREFIXES):
        return await call_next(request)

    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return JSONResponse(
            status_code=401,
            content={
                "error": {
                    "code": "AUTHENTICATION_REQUIRED",
                    "message": "Missing or invalid Authorization header.",
                    "details": {},
                }
            },
        )

    token = auth_header.removeprefix("Bearer ").strip()

    from jose import JWTError
    from jose import jwt as jose_jwt

    from src.core.config import settings

    try:
        payload = jose_jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError:
        return JSONResponse(
            status_code=401,
            content={
                "error": {
                    "code": "AUTHENTICATION_REQUIRED",
                    "message": "Invalid or expired token.",
                    "details": {},
                }
            },
        )

    request.state.user_id = payload.get("sub")
    request.state.username = payload.get("username", "")
    request.state.email = payload.get("email", "")
    request.state.role = payload.get("role", "STANDARD")
    request.state.scopes = payload.get("scopes", [])

    log_module.set_correlation_id(payload.get("jti", log_module.get_correlation_id()))

    return await call_next(request)
