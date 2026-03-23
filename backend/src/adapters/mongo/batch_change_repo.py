from __future__ import annotations

from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

from src.adapters.mongo.base_repository import BaseRepository
from src.models.batch_change import BatchChange, BatchChangeState


class BatchChangeRepository(BaseRepository[BatchChange]):
    collection_name = "batch_changes"
    model_class = BatchChange

    async def find_by_namespace(
        self,
        namespace_id: str,
        states: list[BatchChangeState] | None = None,
        skip: int = 0,
        limit: int = 25,
    ) -> list[BatchChange]:
        filter_: dict[str, Any] = {"namespace_id": namespace_id}
        if states:
            filter_["state"] = {"$in": [s.value for s in states]}
        return await self.find_many(
            filter_,
            skip=skip,
            limit=limit,
            sort=[("created_at", -1)],
        )

    async def find_by_name_in_namespace(
        self, namespace_id: str, name: str
    ) -> BatchChange | None:
        docs = await self.find_many(
            {"namespace_id": namespace_id, "name": name}, limit=1
        )
        return docs[0] if docs else None
