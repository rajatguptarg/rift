from __future__ import annotations

from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorDatabase,
)

from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)

_client: AsyncIOMotorClient | None = None


async def connect() -> None:
    global _client
    _client = AsyncIOMotorClient(settings.mongodb_url)
    # Ping to confirm connection
    await _client.admin.command("ping")
    logger.info("MongoDB connection established", database=settings.mongodb_database)


async def disconnect() -> None:
    global _client
    if _client is not None:
        _client.close()
        _client = None
        logger.info("MongoDB connection closed")


def get_client() -> AsyncIOMotorClient:
    if _client is None:
        raise RuntimeError("MongoDB client is not initialised. Call connect() first.")
    return _client


def get_database() -> AsyncIOMotorDatabase:
    return get_client()[settings.mongodb_database]
