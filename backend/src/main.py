from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from src.adapters.mongo import client as mongo_client
from src.adapters.redis import client as redis_client
from src.api.middleware.auth import auth_middleware
from src.api.middleware.redaction import redaction_middleware
from src.core.config import settings
from src.core.errors import RiftError, generic_error_handler, rift_error_handler
from src.core.logging import configure_logging


def create_app() -> FastAPI:
    configure_logging()

    app = FastAPI(
        title="Rift Batch Changes API",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # ── CORS ──────────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.api_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Custom middleware ─────────────────────────────────────────────────────
    app.add_middleware(BaseHTTPMiddleware, dispatch=auth_middleware)
    app.add_middleware(BaseHTTPMiddleware, dispatch=redaction_middleware)

    # ── Exception handlers ────────────────────────────────────────────────────
    app.add_exception_handler(RiftError, rift_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, generic_error_handler)

    # ── Lifecycle ─────────────────────────────────────────────────────────────
    @app.on_event("startup")
    async def startup() -> None:
        await mongo_client.connect()
        await redis_client.connect()

    @app.on_event("shutdown")
    async def shutdown() -> None:
        await mongo_client.disconnect()
        await redis_client.disconnect()

    # ── Health check ──────────────────────────────────────────────────────────
    @app.get("/health", tags=["ops"])
    async def health() -> dict:
        return {"status": "ok"}

    # ── Routers ───────────────────────────────────────────────────────────────
    from src.api.routes import batch_changes, batch_runs, streams
    from src.api.routes import changesets, webhooks, credentials, templates, audit

    app.include_router(batch_changes.router, prefix="/api/v1", tags=["batch-changes"])
    app.include_router(batch_runs.router, prefix="/api/v1", tags=["batch-runs"])
    app.include_router(streams.router, prefix="/api/v1", tags=["streams"])
    app.include_router(changesets.router, prefix="/api/v1", tags=["changesets"])
    app.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
    app.include_router(credentials.router, prefix="/api/v1", tags=["credentials"])
    app.include_router(templates.router, prefix="/api/v1", tags=["templates"])
    app.include_router(audit.router, prefix="/api/v1", tags=["audit"])

    return app


app = create_app()
