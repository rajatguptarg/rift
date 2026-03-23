from __future__ import annotations

import uuid
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorDatabase

from src.adapters.mongo.batch_change_repo import BatchChangeRepository
from src.adapters.mongo.batch_spec_repo import BatchSpecRepository
from src.core.errors import ConflictError, StateTransitionError
from src.core.logging import get_logger
from src.models.batch_change import BatchChange, BatchChangeCreate, BatchChangeState
from src.models.batch_spec import BatchSpec

logger = get_logger(__name__)


class BatchChangeService:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self._repo = BatchChangeRepository(db)
        self._spec_repo = BatchSpecRepository(db)

    async def create(self, data: BatchChangeCreate, created_by: str) -> BatchChange:
        existing = await self._repo.find_by_name_in_namespace(
            data.namespace_id, data.name
        )
        if existing:
            raise ConflictError(
                f"Batch change '{data.name}' already exists in namespace '{data.namespace_id}'"
            )
        bc = BatchChange(
            id=f"bc_{uuid.uuid4().hex[:12]}",
            namespace_id=data.namespace_id,
            name=data.name,
            description=data.description,
            source_mode=data.source_mode,
            created_by=created_by,
        )
        return await self._repo.insert(bc)

    async def get(self, batch_change_id: str) -> BatchChange:
        return await self._repo.get_by_id(batch_change_id)

    async def list_by_namespace(
        self,
        namespace_id: str,
        states: list[BatchChangeState] | None = None,
        skip: int = 0,
        limit: int = 25,
    ) -> list[BatchChange]:
        return await self._repo.find_by_namespace(namespace_id, states, skip, limit)

    async def update_spec(
        self, batch_change_id: str, spec_yaml: str, version: int
    ) -> tuple[BatchChange, BatchSpec]:
        await self._repo.get_by_id(batch_change_id)

        spec = BatchSpec(
            id=f"bs_{uuid.uuid4().hex[:12]}",
            batch_change_id=batch_change_id,
            spec_yaml=spec_yaml,
        )
        spec = await self._spec_repo.insert(spec)

        updated = await self._repo.update_with_version(
            batch_change_id,
            version,
            {
                "active_spec_id": spec.id,
                "updated_at": datetime.utcnow().isoformat(),
            },
        )
        logger.info("BatchChange spec updated", id=batch_change_id, spec_id=spec.id)
        return updated, spec

    async def transition_state(
        self, batch_change_id: str, new_state: BatchChangeState, version: int
    ) -> BatchChange:
        bc = await self._repo.get_by_id(batch_change_id)
        if not bc.can_transition_to(new_state):
            raise StateTransitionError(
                f"BatchChange:{batch_change_id}", bc.state.value, new_state.value
            )
        extra: dict = {"updated_at": datetime.utcnow().isoformat()}
        if new_state == BatchChangeState.ARCHIVED:
            extra["archived_at"] = datetime.utcnow().isoformat()
        return await self._repo.update_with_version(
            batch_change_id, version, {"state": new_state.value, **extra}
        )

    async def close(self, batch_change_id: str, version: int) -> BatchChange:
        return await self.transition_state(
            batch_change_id, BatchChangeState.ARCHIVED, version
        )

    async def archive(self, batch_change_id: str, version: int) -> BatchChange:
        return await self.transition_state(
            batch_change_id, BatchChangeState.ARCHIVED, version
        )

    async def pause(self, batch_change_id: str, version: int) -> BatchChange:
        return await self.transition_state(
            batch_change_id, BatchChangeState.PAUSED, version
        )

    async def resume(self, batch_change_id: str, version: int) -> BatchChange:
        return await self.transition_state(
            batch_change_id, BatchChangeState.ACTIVE, version
        )
