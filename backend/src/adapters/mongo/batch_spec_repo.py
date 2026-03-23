from __future__ import annotations

from src.adapters.mongo.base_repository import BaseRepository
from src.models.batch_spec import BatchSpec


class BatchSpecRepository(BaseRepository[BatchSpec]):
    collection_name = "batch_specs"
    model_class = BatchSpec

    async def find_by_batch_change(
        self, batch_change_id: str, limit: int = 10
    ) -> list[BatchSpec]:
        return await self.find_many(
            {"batch_change_id": batch_change_id},
            limit=limit,
            sort=[("created_at", -1)],
        )

    async def find_by_hash(self, spec_hash: str) -> BatchSpec | None:
        docs = await self.find_many({"spec_hash": spec_hash}, limit=1)
        return docs[0] if docs else None
