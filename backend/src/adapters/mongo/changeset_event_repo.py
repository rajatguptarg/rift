from __future__ import annotations

from src.adapters.mongo.base_repository import BaseRepository
from src.models.changeset import ChangesetEvent


class ChangesetEventRepository(BaseRepository[ChangesetEvent]):
    collection_name = "changeset_events"
    model_class = ChangesetEvent

    async def find_by_changeset(
        self, changeset_id: str, limit: int = 50
    ) -> list[ChangesetEvent]:
        return await self.find_many(
            {"changeset_id": changeset_id},
            limit=limit,
            sort=[("occurred_at", -1)],
        )
