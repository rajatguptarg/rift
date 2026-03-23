from __future__ import annotations

from typing import Any

from src.adapters.mongo.base_repository import BaseRepository
from src.models.execution import WorkspaceExecution, WorkspaceExecutionState


class WorkspaceExecutionRepository(BaseRepository[WorkspaceExecution]):
    collection_name = "workspace_executions"
    model_class = WorkspaceExecution

    async def find_by_run(
        self,
        batch_run_id: str,
        states: list[WorkspaceExecutionState] | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[WorkspaceExecution]:
        filter_: dict[str, Any] = {"batch_run_id": batch_run_id}
        if states:
            filter_["state"] = {"$in": [s.value for s in states]}
        return await self.find_many(filter_, skip=skip, limit=limit)

    async def mark_excluded(self, execution_id: str) -> None:
        await self._collection.update_one(
            {"_id": execution_id}, {"$set": {"is_excluded": True}}
        )
