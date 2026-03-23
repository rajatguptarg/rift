from __future__ import annotations

import uuid
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorDatabase

from src.adapters.mongo.base_repository import BaseRepository
from src.models.audit import AuditAction, AuditEvent


class _AuditRepository(BaseRepository[AuditEvent]):
    collection_name = "audit_events"
    model_class = AuditEvent


class AuditService:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self._repo = _AuditRepository(db)

    async def record(
        self,
        actor_id: str,
        resource_type: str,
        resource_id: str,
        action: AuditAction,
        payload: dict | None = None,
    ) -> AuditEvent:
        event = AuditEvent(
            id=f"ae_{uuid.uuid4().hex[:12]}",
            actor_id=actor_id,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            payload=payload or {},
        )
        return await self._repo.insert(event)

    async def list_events(
        self,
        resource_type: str | None = None,
        resource_id: str | None = None,
        actor_id: str | None = None,
        limit: int = 50,
    ) -> list[AuditEvent]:
        filter_: dict = {}
        if resource_type:
            filter_["resource_type"] = resource_type
        if resource_id:
            filter_["resource_id"] = resource_id
        if actor_id:
            filter_["actor_id"] = actor_id
        return await self._repo.find_many(
            filter_, limit=limit, sort=[("occurred_at", -1)]
        )
