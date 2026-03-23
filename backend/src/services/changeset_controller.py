from __future__ import annotations

import uuid
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorDatabase

from src.adapters.mongo.changeset_event_repo import ChangesetEventRepository
from src.adapters.mongo.changeset_repo import ChangesetRepository
from src.adapters.mongo.changeset_spec_repo import ChangesetSpecRepository
from src.core.logging import get_logger
from src.models.changeset import (
    Changeset,
    ChangesetEvent,
    ChangesetState,
    CIState,
    ReviewDecision,
)
from src.models.changeset_spec import ChangesetSpec, ChangesetSpecState, PublishMode

logger = get_logger(__name__)


class ChangesetController:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self._cs_repo = ChangesetRepository(db)
        self._spec_repo = ChangesetSpecRepository(db)
        self._event_repo = ChangesetEventRepository(db)

    async def publish(
        self,
        changeset_spec_id: str,
        publish_mode: PublishMode,
    ) -> Changeset:
        spec = await self._spec_repo.get_by_id(changeset_spec_id)

        changeset = Changeset(
            id=f"ch_{uuid.uuid4().hex[:12]}",
            changeset_spec_id=spec.id,
            batch_change_id=spec.batch_change_id,
            repo_ref=spec.repo_ref,
            state=(
                ChangesetState.OPEN
                if publish_mode != PublishMode.DRAFT_PR
                else ChangesetState.DRAFT
            ),
            title=spec.title,
            branch=spec.branch,
        )
        changeset = await self._cs_repo.insert(changeset)

        event = ChangesetEvent(
            id=f"ce_{uuid.uuid4().hex[:12]}",
            changeset_id=changeset.id,
            event_type="published",
            payload={"publish_mode": publish_mode},
        )
        await self._event_repo.insert(event)
        logger.info("Changeset published", id=changeset.id, mode=publish_mode)
        return changeset

    async def bulk_publish(
        self,
        batch_change_id: str,
        publish_mode: PublishMode,
    ) -> list[Changeset]:
        specs = await self._spec_repo.find_by_batch_change(batch_change_id)
        publishable = [s for s in specs if s.state == ChangesetSpecState.UNPUBLISHED]
        results = []
        for spec in publishable:
            try:
                cs = await self.publish(spec.id, publish_mode)
                results.append(cs)
            except Exception:
                logger.exception("Failed to publish changeset spec", spec_id=spec.id)
        return results

    async def bulk_close(
        self,
        batch_change_id: str,
        changeset_ids: list[str],
    ) -> list[Changeset]:
        results = []
        for cid in changeset_ids:
            await self._cs_repo.get_by_id(cid)
            updated = await self._cs_repo.update_with_version(
                cid, 0,
                {"state": ChangesetState.CLOSED, "closed_at": datetime.utcnow().isoformat()},
            )
            results.append(updated)
        return results

    async def sync_status(
        self,
        changeset_id: str,
        state: ChangesetState | None,
        review_state: ReviewDecision | None,
        ci_state: CIState | None,
        merged_at: datetime | None = None,
    ) -> Changeset:
        fields: dict = {"updated_at": datetime.utcnow().isoformat()}
        if state:
            fields["state"] = state.value
        if review_state:
            fields["review_state"] = review_state.value
        if ci_state:
            fields["ci_state"] = ci_state.value
        if merged_at:
            fields["merged_at"] = merged_at.isoformat()

        return await self._cs_repo.update_with_version(changeset_id, 0, fields)

    async def import_external(
        self,
        batch_change_id: str,
        external_url: str,
        repo_ref: str,
        external_id: str,
        title: str,
        branch: str,
    ) -> Changeset:
        spec = ChangesetSpec(
            id=f"cs_{uuid.uuid4().hex[:12]}",
            batch_change_id=batch_change_id,
            repo_ref=repo_ref,
            diff_key="",
            branch=branch,
            title=title,
            state=ChangesetSpecState.PUBLISHED,
            external_pr_url=external_url,
        )
        spec = await self._spec_repo.insert(spec)

        cs = Changeset(
            id=f"ch_{uuid.uuid4().hex[:12]}",
            changeset_spec_id=spec.id,
            batch_change_id=batch_change_id,
            repo_ref=repo_ref,
            external_id=external_id,
            external_url=external_url,
            state=ChangesetState.OPEN,
            title=title,
            branch=branch,
        )
        return await self._cs_repo.insert(cs)
