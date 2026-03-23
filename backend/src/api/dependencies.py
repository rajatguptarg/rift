from __future__ import annotations

from typing import Annotated

import redis.asyncio as aioredis
from fastapi import Depends, HTTPException, Request
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.adapters.mongo.client import get_database
from src.adapters.redis.client import get_redis
from src.core.errors import AuthenticationError
from src.models.user import User


# ── Database ─────────────────────────────────────────────────────────────────

def get_db() -> AsyncIOMotorDatabase:
    return get_database()


DBDep = Annotated[AsyncIOMotorDatabase, Depends(get_db)]


# ── Redis ────────────────────────────────────────────────────────────────────

def get_redis_dep() -> aioredis.Redis:
    return get_redis()


RedisDep = Annotated[aioredis.Redis, Depends(get_redis_dep)]


# ── Current User ─────────────────────────────────────────────────────────────

async def get_current_user(request: Request) -> User:
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return User(
        id=user_id,
        email=getattr(request.state, "email", ""),
        display_name="",
        auth_subject=user_id,
    )


CurrentUserDep = Annotated[User, Depends(get_current_user)]


# ── Namespace ─────────────────────────────────────────────────────────────────

async def get_namespace_id(
    namespace: str | None = None,
    current_user: User = Depends(get_current_user),
) -> str:
    """Resolve namespace from query param or fall back to user's personal namespace."""
    if namespace:
        return namespace
    return f"ns_{current_user.id}"


NamespaceDep = Annotated[str, Depends(get_namespace_id)]
