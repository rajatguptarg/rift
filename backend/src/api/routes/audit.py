from __future__ import annotations

from fastapi import APIRouter, Query

from src.api.dependencies import CurrentUserDep, DBDep
from src.models.audit import AuditEventResponse
from src.services.audit_service import AuditService

router = APIRouter()


@router.get("/audit-events", response_model=list[AuditEventResponse])
async def list_audit_events(
    db: DBDep,
    current_user: CurrentUserDep,
    resource_type: str | None = Query(default=None),
    resource_id: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
) -> list[AuditEventResponse]:
    svc = AuditService(db)
    events = await svc.list_events(
        resource_type=resource_type,
        resource_id=resource_id,
        limit=limit,
    )
    return [AuditEventResponse(**evt.model_dump()) for evt in events]
