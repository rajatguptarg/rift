from __future__ import annotations

from fastapi import APIRouter, Query

from src.api.dependencies import CurrentUserDep, DBDep, NamespaceDep
from src.models.batch_change import BatchChangeCreate, BatchChangeResponse, BatchChangeState
from src.models.batch_spec import BatchSpecResponse
from src.models.common import CursorPage
from src.models.execution import BatchRunResponse
from src.services.batch_change_service import BatchChangeService
from src.services.execution_orchestrator import ExecutionOrchestrator

router = APIRouter()


@router.get("/batch-changes", response_model=CursorPage[BatchChangeResponse])
async def list_batch_changes(
    db: DBDep,
    current_user: CurrentUserDep,
    namespace: NamespaceDep,
    state: list[BatchChangeState] | None = Query(default=None),
    limit: int = Query(default=25, ge=1, le=100),
) -> CursorPage[BatchChangeResponse]:
    svc = BatchChangeService(db)
    items = await svc.list_by_namespace(namespace, state, limit=limit)
    return CursorPage(items=[BatchChangeResponse(**bc.model_dump()) for bc in items])


@router.post("/batch-changes", response_model=BatchChangeResponse, status_code=201)
async def create_batch_change(
    body: BatchChangeCreate,
    db: DBDep,
    current_user: CurrentUserDep,
) -> BatchChangeResponse:
    svc = BatchChangeService(db)
    bc = await svc.create(body, created_by=current_user.id)
    return BatchChangeResponse(**bc.model_dump())


@router.get("/batch-changes/{batch_change_id}", response_model=BatchChangeResponse)
async def get_batch_change(
    batch_change_id: str, db: DBDep, current_user: CurrentUserDep
) -> BatchChangeResponse:
    svc = BatchChangeService(db)
    bc = await svc.get(batch_change_id)
    return BatchChangeResponse(**bc.model_dump())


@router.patch(
    "/batch-changes/{batch_change_id}/spec", response_model=BatchSpecResponse
)
async def update_batch_spec(
    batch_change_id: str,
    body: dict,
    db: DBDep,
    current_user: CurrentUserDep,
) -> BatchSpecResponse:
    svc = BatchChangeService(db)
    _, spec = await svc.update_spec(
        batch_change_id,
        spec_yaml=body["spec_yaml"],
        version=body.get("version", 0),
    )
    return BatchSpecResponse(**spec.model_dump())


@router.post(
    "/batch-changes/{batch_change_id}/preview", response_model=BatchRunResponse
)
async def run_preview(
    batch_change_id: str,
    body: dict,
    db: DBDep,
    current_user: CurrentUserDep,
) -> BatchRunResponse:
    svc = BatchChangeService(db)
    bc = await svc.get(batch_change_id)

    orchestrator = ExecutionOrchestrator(db)
    run = await orchestrator.trigger_preview(
        batch_change_id=batch_change_id,
        batch_spec_id=bc.active_spec_id or "",
        repo_refs=body.get("repo_refs", []),
        skip_errors=body.get("skip_errors", False),
    )
    return BatchRunResponse(**run.model_dump())


@router.post(
    "/batch-changes/{batch_change_id}/apply", response_model=BatchRunResponse
)
async def apply_batch_change(
    batch_change_id: str,
    db: DBDep,
    current_user: CurrentUserDep,
) -> BatchRunResponse:
    svc = BatchChangeService(db)
    bc = await svc.get(batch_change_id)

    orchestrator = ExecutionOrchestrator(db)
    run = await orchestrator.trigger_apply(
        batch_change_id=batch_change_id,
        batch_spec_id=bc.active_spec_id or "",
    )
    return BatchRunResponse(**run.model_dump())


@router.post("/batch-changes/{batch_change_id}/close", response_model=BatchChangeResponse)
async def close_batch_change(
    batch_change_id: str, body: dict, db: DBDep, current_user: CurrentUserDep
) -> BatchChangeResponse:
    svc = BatchChangeService(db)
    bc = await svc.close(batch_change_id, version=body.get("version", 0))
    return BatchChangeResponse(**bc.model_dump())


@router.post("/batch-changes/{batch_change_id}/archive", response_model=BatchChangeResponse)
async def archive_batch_change(
    batch_change_id: str, body: dict, db: DBDep, current_user: CurrentUserDep
) -> BatchChangeResponse:
    svc = BatchChangeService(db)
    bc = await svc.archive(batch_change_id, version=body.get("version", 0))
    return BatchChangeResponse(**bc.model_dump())
