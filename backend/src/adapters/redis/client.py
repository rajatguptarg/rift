from __future__ import annotations

import redis.asyncio as aioredis

from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)

_redis: aioredis.Redis | None = None


async def connect() -> None:
    global _redis
    _redis = aioredis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
    )
    await _redis.ping()
    logger.info("Redis connection established")


async def disconnect() -> None:
    global _redis
    if _redis is not None:
        await _redis.aclose()
        _redis = None
        logger.info("Redis connection closed")


def get_redis() -> aioredis.Redis:
    if _redis is None:
        raise RuntimeError("Redis client is not initialised. Call connect() first.")
    return _redis
