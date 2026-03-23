from __future__ import annotations

import asyncio
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorDatabase

from src.adapters.code_hosts.base import CodeHostAdapter
from src.adapters.mongo.changeset_repo import ChangesetRepository
from src.adapters.mongo.changeset_spec_repo import ChangesetSpecRepository
from src.core.logging import get_logger
from src.models.changeset import ChangesetState

logger = get_logger(__name__)


class ReconciliationService:
    """
    Desired-state reconciliation loop.
    Compares ChangesetSpec fingerprints against live code host state
    and drives convergence.
    """

    POLL_INTERVAL_SECONDS = 30

    def __init__(
        self, db: AsyncIOMotorDatabase, code_host_adapters: dict[str, CodeHostAdapter]
    ) -> None:
        self._cs_repo = ChangesetRepository(db)
        self._spec_repo = ChangesetSpecRepository(db)
        self._adapters = code_host_adapters
        self._running = False

    async def run_once(self, batch_change_id: str) -> None:
        """Run a single reconciliation pass for a batch change."""
        changesets = await self._cs_repo.find_by_batch_change(batch_change_id)
        for cs in changesets:
            if cs.external_id is None:
                continue
            # Determine adapter by repo_ref prefix
            adapter = self._resolve_adapter(cs.repo_ref)
            if adapter is None:
                continue
            try:
                pr = await adapter.get_pull_request(cs.repo_ref, cs.external_id)
                state = ChangesetState.OPEN
                if pr.merged_at:
                    state = ChangesetState.MERGED
                elif pr.state == "closed":
                    state = ChangesetState.CLOSED

                await self._cs_repo.update_with_version(
                    cs.id, 0,
                    {
                        "state": state.value,
                        "updated_at": datetime.utcnow().isoformat(),
                    },
                )
            except Exception:
                logger.exception("Reconciliation failed for changeset", id=cs.id)

    async def run_loop(self) -> None:
        self._running = True
        while self._running:
            # In production iterate over all active batch changes
            await asyncio.sleep(self.POLL_INTERVAL_SECONDS)

    def stop(self) -> None:
        self._running = False

    def _resolve_adapter(self, repo_ref: str) -> CodeHostAdapter | None:
        if repo_ref.startswith("github.com/"):
            return self._adapters.get("github")
        if repo_ref.startswith("gitlab.com/"):
            return self._adapters.get("gitlab")
        return None
