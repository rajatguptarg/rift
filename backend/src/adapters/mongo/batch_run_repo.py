from __future__ import annotations

from src.adapters.mongo.base_repository import BaseRepository
from src.models.execution import BatchRun, BatchRunState


class BatchRunRepository(BaseRepository[BatchRun]):
    collection_name = "batch_runs"
    model_class = BatchRun

    async def find_by_batch_change(
        self, batch_change_id: str, limit: int = 10
    ) -> list[BatchRun]:
        return await self.find_many(
            {"batch_change_id": batch_change_id},
            limit=limit,
            sort=[("created_at", -1)],
        )

    async def find_latest(self, batch_change_id: str) -> BatchRun | None:
        runs = await self.find_by_batch_change(batch_change_id, limit=1)
        return runs[0] if runs else None
