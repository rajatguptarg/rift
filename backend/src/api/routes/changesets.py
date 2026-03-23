from __future__ import annotations

from fastapi import APIRouter, Query

from src.api.dependencies import CurrentUserDep, DBDep
from src.models.analytics import BurndownResponse, StatsResponse
from src.models.changeset import ChangesetResponse, ChangesetState, CIState, ReviewDecision
from src.models.changeset_spec import PublishMode
from src.models.common import CursorPage
from src.services.analytics_service import AnalyticsService
from src.services.changeset_controller import ChangesetController

router = APIRouter()


@router.get(
    "/batch-changes/{batch_change_id}/changesets",
    response_model=CursorPage[ChangesetResponse],
)
async def list_changesets(
    batch_change_id: str,
    db: DBDep,
    current_user: CurrentUserDep,
    state: list[ChangesetState] | None = Query(default=None),
    review_state: ReviewDecision | None = Query(default=None),
    ci_state: CIState | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
) -> CursorPage[ChangesetResponse]:
    from src.adapters.mongo.changeset_repo import ChangesetRepository
    repo = ChangesetRepository(db)
    items = await repo.find_by_batch_change(
        batch_change_id,
        states=state,
        review_state=review_state,
        ci_state=ci_state,
        limit=limit,
    )
    return CursorPage(items=[ChangesetResponse(**cs.model_dump()) for cs in items])


@router.post(
    "/batch-changes/{batch_change_id}/changesets/publish",
    response_model=list[ChangesetResponse],
)
async def publish_changesets(
    batch_change_id: str,
    body: dict,
    db: DBDep,
    current_user: CurrentUserDep,
) -> list[ChangesetResponse]:
    ctrl = ChangesetController(db)
    mode = PublishMode(body.get("publish_mode", PublishMode.FULL_PR))
    items = await ctrl.bulk_publish(batch_change_id, mode)
    return [ChangesetResponse(**cs.model_dump()) for cs in items]


@router.get(
    "/batch-changes/{batch_change_id}/stats",
    response_model=StatsResponse,
)
async def get_stats(
    batch_change_id: str, db: DBDep, current_user: CurrentUserDep
) -> StatsResponse:
    svc = AnalyticsService(db)
    stats = await svc.compute_stats(batch_change_id)
    return StatsResponse(**stats.model_dump())


@router.get(
    "/batch-changes/{batch_change_id}/burndown",
    response_model=BurndownResponse,
)
async def get_burndown(
    batch_change_id: str,
    db: DBDep,
    current_user: CurrentUserDep,
    days: int = Query(default=30, ge=7, le=90),
) -> BurndownResponse:
    svc = AnalyticsService(db)
    data = await svc.compute_burndown(batch_change_id, days=days)
    return BurndownResponse(batch_change_id=batch_change_id, data=data)


@router.post(
    "/batch-changes/{batch_change_id}/changesets/import",
    response_model=list[ChangesetResponse],
    status_code=201,
)
async def import_changesets(
    batch_change_id: str,
    body: dict,
    db: DBDep,
    current_user: CurrentUserDep,
) -> list[ChangesetResponse]:
    """Import externally-created PRs/MRs into a batch change for unified tracking."""
    ctrl = ChangesetController(db)
    results = []
    for entry in body.get("urls", []):
        url = entry if isinstance(entry, str) else entry.get("url", "")
        # Parse repo_ref and external_id from URL (simplified)
        parts = url.rstrip("/").split("/")
        external_id = parts[-1]
        repo_ref = "/".join(parts[-4:-2]) if len(parts) >= 4 else url
        cs = await ctrl.import_external(
            batch_change_id=batch_change_id,
            external_url=url,
            repo_ref=repo_ref,
            external_id=external_id,
            title=f"Imported PR #{external_id}",
            branch="main",
        )
        results.append(ChangesetResponse(**cs.model_dump()))
    return results
