from __future__ import annotations

from typing import Any

from src.adapters.mongo.base_repository import BaseRepository
from src.models.changeset import Changeset, ChangesetState, CIState, ReviewDecision


class ChangesetRepository(BaseRepository[Changeset]):
    collection_name = "changesets"
    model_class = Changeset

    async def find_by_batch_change(
        self,
        batch_change_id: str,
        states: list[ChangesetState] | None = None,
        review_state: ReviewDecision | None = None,
        ci_state: CIState | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Changeset]:
        filter_: dict[str, Any] = {"batch_change_id": batch_change_id}
        if states:
            filter_["state"] = {"$in": [s.value for s in states]}
        if review_state:
            filter_["review_state"] = review_state.value
        if ci_state:
            filter_["ci_state"] = ci_state.value
        return await self.find_many(filter_, skip=skip, limit=limit)

    async def find_by_external_id(
        self, repo_ref: str, external_id: str
    ) -> Changeset | None:
        docs = await self.find_many(
            {"repo_ref": repo_ref, "external_id": external_id}, limit=1
        )
        return docs[0] if docs else None
