from __future__ import annotations

from src.adapters.mongo.base_repository import BaseRepository
from src.models.user import User


class UserRepository(BaseRepository[User]):
    collection_name = "users"
    model_class = User

    async def find_by_username(self, username: str) -> User | None:
        doc = await self._collection.find_one({"username": username.lower()})
        if doc is None:
            return None
        return self._from_doc(doc)

    async def find_bootstrap_user(self) -> User | None:
        doc = await self._collection.find_one({"bootstrap_managed": True})
        if doc is None:
            return None
        return self._from_doc(doc)

    async def update_last_login(self, user_id: str, last_login_at) -> None:  # type: ignore[type-arg]
        from datetime import datetime

        await self._collection.update_one(
            {"_id": user_id},
            {"$set": {"last_login_at": last_login_at, "updated_at": datetime.utcnow()}},
        )

    async def ensure_unique_username_index(self) -> None:
        await self._collection.create_index("username", unique=True)
