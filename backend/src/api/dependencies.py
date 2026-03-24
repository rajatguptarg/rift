from __future__ import annotations

from typing import Annotated

import redis.asyncio as aioredis
from fastapi import Depends, HTTPException, Request
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.adapters.mongo.client import get_database
from src.adapters.redis.client import get_redis
from src.models.user import AccessRole, User

# ── Database ─────────────────────────────────────────────────────────────────

def get_db() -> AsyncIOMotorDatabase:
    return get_database()


DBDep = Annotated[AsyncIOMotorDatabase, Depends(get_db)]


# ── Redis ────────────────────────────────────────────────────────────────────

def get_redis_dep() -> aioredis.Redis:
    return get_redis()


RedisDep = Annotated[aioredis.Redis, Depends(get_redis_dep)]


# ── Current User ─────────────────────────────────────────────────────────────

async def get_current_user(
    request: Request,
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> User:
    user_id = getattr(request.state, "user_id", None)
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    from src.adapters.mongo.user_repo import UserRepository

    repo = UserRepository(db)
    user = await repo.find_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]


# ── Super User Guard ─────────────────────────────────────────────────────────

async def require_super_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != AccessRole.SUPER_USER:
        raise HTTPException(status_code=403, detail="Super user access required")
    return current_user


SuperUserDep = Annotated[User, Depends(require_super_user)]


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
