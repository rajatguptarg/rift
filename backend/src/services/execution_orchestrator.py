from __future__ import annotations

import uuid

from motor.motor_asyncio import AsyncIOMotorDatabase
from temporalio.client import Client

from src.adapters.mongo.batch_change_repo import BatchChangeRepository
from src.adapters.mongo.batch_run_repo import BatchRunRepository
from src.adapters.mongo.workspace_execution_repo import WorkspaceExecutionRepository
from src.core.config import settings
from src.core.logging import get_logger
from src.models.batch_change import BatchChangeState
from src.models.execution import BatchRun, BatchRunState, WorkspaceExecution

logger = get_logger(__name__)


class ExecutionOrchestrator:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self._bc_repo = BatchChangeRepository(db)
        self._run_repo = BatchRunRepository(db)
        self._we_repo = WorkspaceExecutionRepository(db)

    async def _get_temporal_client(self) -> Client:
        return await Client.connect(
            settings.temporal_host, namespace=settings.temporal_namespace
        )

    async def trigger_preview(
        self,
        batch_change_id: str,
        batch_spec_id: str,
        repo_refs: list[str],
        skip_errors: bool = False,
    ) -> BatchRun:
        run = BatchRun(
            id=f"br_{uuid.uuid4().hex[:12]}",
            batch_change_id=batch_change_id,
            batch_spec_id=batch_spec_id,
            state=BatchRunState.PENDING,
            total_workspaces=len(repo_refs),
            skip_errors=skip_errors,
        )
        run = await self._run_repo.insert(run)

        # Create workspace execution records
        for repo_ref in repo_refs:
            we = WorkspaceExecution(
                id=f"we_{uuid.uuid4().hex[:12]}",
                batch_run_id=run.id,
                repo_ref=repo_ref,
            )
            await self._we_repo.insert(we)

        # Kick off Temporal workflow
        try:
            client = await self._get_temporal_client()
            wf_id = f"preview-{run.id}"
            await client.start_workflow(
                "PreviewWorkflow",
                args=[run.id, batch_spec_id, repo_refs, skip_errors],
                id=wf_id,
                task_queue=settings.temporal_task_queue,
            )
            await self._run_repo.update_with_version(
                run.id, 0, {"temporal_workflow_id": wf_id, "state": BatchRunState.RUNNING}
            )
        except Exception:
            logger.exception("Failed to start Temporal workflow", run_id=run.id)
            await self._run_repo.update_with_version(
                run.id, 0, {"state": BatchRunState.FAILED}
            )

        # Transition batch change to PREVIEW_RUNNING
        bc = await self._bc_repo.get_by_id(batch_change_id)
        await self._bc_repo.update_with_version(
            batch_change_id,
            bc.version,
            {"state": BatchChangeState.PREVIEW_RUNNING},
        )

        return run

    async def trigger_apply(
        self, batch_change_id: str, batch_spec_id: str
    ) -> BatchRun:
        run = BatchRun(
            id=f"br_{uuid.uuid4().hex[:12]}",
            batch_change_id=batch_change_id,
            batch_spec_id=batch_spec_id,
            state=BatchRunState.PENDING,
        )
        run = await self._run_repo.insert(run)

        try:
            client = await self._get_temporal_client()
            wf_id = f"apply-{run.id}"
            await client.start_workflow(
                "ApplyWorkflow",
                args=[run.id, batch_change_id, batch_spec_id],
                id=wf_id,
                task_queue=settings.temporal_task_queue,
            )
            await self._run_repo.update_with_version(
                run.id, 0, {"temporal_workflow_id": wf_id, "state": BatchRunState.RUNNING}
            )
        except Exception:
            logger.exception("Failed to start apply Temporal workflow", run_id=run.id)
            await self._run_repo.update_with_version(
                run.id, 0, {"state": BatchRunState.FAILED}
            )

        bc = await self._bc_repo.get_by_id(batch_change_id)
        await self._bc_repo.update_with_version(
            batch_change_id, bc.version, {"state": BatchChangeState.APPLYING}
        )

        return run

    async def cancel(self, batch_run_id: str) -> None:
        run = await self._run_repo.get_by_id(batch_run_id)
        if run.temporal_workflow_id:
            try:
                client = await self._get_temporal_client()
                handle = client.get_workflow_handle(run.temporal_workflow_id)
                await handle.cancel()
            except Exception:
                logger.exception("Failed to cancel Temporal workflow", run_id=batch_run_id)
        await self._run_repo.update_with_version(
            batch_run_id, run.version if hasattr(run, "version") else 0,
            {"state": BatchRunState.CANCELLED}
        )
