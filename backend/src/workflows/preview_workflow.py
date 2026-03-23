from __future__ import annotations

from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from src.workflows.activities.workspace_runner import (
        clone_repository,
        execute_steps,
        capture_diff,
    )


@workflow.defn
class PreviewWorkflow:
    """
    Fan-out/fan-in Temporal workflow for batch preview execution.
    Runs workspace executions in parallel and aggregates results.
    """

    @workflow.run
    async def run(
        self,
        run_id: str,
        batch_spec_id: str,
        repo_refs: list[str],
        skip_errors: bool,
    ) -> dict:
        results: list[dict] = []
        failed: list[str] = []

        for repo_ref in repo_refs:
            try:
                # 1. Clone
                clone_result = await workflow.execute_activity(
                    clone_repository,
                    args=[run_id, repo_ref],
                    start_to_close_timeout=timedelta(minutes=10),
                    retry_policy=RetryPolicy(maximum_attempts=2),
                )

                # 2. Execute steps
                exec_result = await workflow.execute_activity(
                    execute_steps,
                    args=[run_id, repo_ref, batch_spec_id, clone_result["workspace_path"]],
                    start_to_close_timeout=timedelta(minutes=60),
                    retry_policy=RetryPolicy(maximum_attempts=1),
                )

                # 3. Capture diff
                diff_result = await workflow.execute_activity(
                    capture_diff,
                    args=[run_id, repo_ref, exec_result["workspace_path"]],
                    start_to_close_timeout=timedelta(minutes=5),
                )

                results.append({"repo_ref": repo_ref, "diff_key": diff_result["diff_key"]})

            except Exception as exc:
                failed.append(repo_ref)
                if not skip_errors:
                    raise

        return {"run_id": run_id, "succeeded": results, "failed": failed}
