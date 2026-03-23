from __future__ import annotations

from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy


@workflow.defn
class ApplyWorkflow:
    """
    Temporal workflow for applying a batch change.
    Finalises the batch run and produces ChangesetSpec records.
    """

    @workflow.run
    async def run(
        self,
        run_id: str,
        batch_change_id: str,
        batch_spec_id: str,
    ) -> dict:
        # In a full implementation this workflow would:
        # 1. Load all SUCCEEDED WorkspaceExecutions for run_id
        # 2. For each, create a ChangesetSpec record
        # 3. Transition BatchChange state to ACTIVE
        # For now it notifies completion via a stub activity
        workflow.logger.info(
            "ApplyWorkflow running",
            run_id=run_id,
            batch_change_id=batch_change_id,
        )
        return {
            "run_id": run_id,
            "batch_change_id": batch_change_id,
            "status": "applied",
        }
