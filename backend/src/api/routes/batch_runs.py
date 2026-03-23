from __future__ import annotations

from fastapi import APIRouter

from src.api.dependencies import CurrentUserDep, DBDep
from src.adapters.mongo.batch_run_repo import BatchRunRepository
from src.adapters.mongo.workspace_execution_repo import WorkspaceExecutionRepository
from src.models.execution import BatchRunResponse, WorkspaceExecutionResponse

router = APIRouter()


@router.get("/batch-changes/{batch_change_id}/runs/{run_id}", response_model=BatchRunResponse)
async def get_batch_run(
    batch_change_id: str, run_id: str, db: DBDep, current_user: CurrentUserDep
) -> BatchRunResponse:
    repo = BatchRunRepository(db)
    run = await repo.get_by_id(run_id)
    return BatchRunResponse(**run.model_dump())


@router.get(
    "/batch-changes/{batch_change_id}/runs/{run_id}/workspaces",
    response_model=list[WorkspaceExecutionResponse],
)
async def list_workspace_executions(
    batch_change_id: str,
    run_id: str,
    db: DBDep,
    current_user: CurrentUserDep,
) -> list[WorkspaceExecutionResponse]:
    repo = WorkspaceExecutionRepository(db)
    items = await repo.find_by_run(run_id)
    return [WorkspaceExecutionResponse(**we.model_dump()) for we in items]


@router.post(
    "/batch-changes/{batch_change_id}/runs/{run_id}/workspaces/{workspace_id}/exclude",
    response_model=dict,
)
async def exclude_workspace(
    batch_change_id: str,
    run_id: str,
    workspace_id: str,
    db: DBDep,
    current_user: CurrentUserDep,
) -> dict:
    repo = WorkspaceExecutionRepository(db)
    await repo.mark_excluded(workspace_id)
    return {"excluded": True}
