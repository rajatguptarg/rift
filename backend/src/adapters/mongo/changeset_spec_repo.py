from __future__ import annotations

from typing import Any

from src.adapters.mongo.base_repository import BaseRepository
from src.models.changeset_spec import ChangesetSpec


class ChangesetSpecRepository(BaseRepository[ChangesetSpec]):
    collection_name = "changeset_specs"
    model_class = ChangesetSpec

    async def find_by_batch_change(
        self,
        batch_change_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ChangesetSpec]:
        return await self.find_many(
            {"batch_change_id": batch_change_id},
            skip=skip,
            limit=limit,
            sort=[("created_at", -1)],
        )

    async def find_by_batch_change_and_repo(
        self, batch_change_id: str, repo_ref: str
    ) -> ChangesetSpec | None:
        docs = await self.find_many(
            {"batch_change_id": batch_change_id, "repo_ref": repo_ref}, limit=1
        )
        return docs[0] if docs else None
