from __future__ import annotations

import subprocess
import tempfile
import os

from temporalio import activity

from src.core.logging import get_logger

logger = get_logger(__name__)


@activity.defn
async def clone_repository(run_id: str, repo_ref: str) -> dict:
    """Clone a repository into a temporary workspace directory."""
    workspace_path = tempfile.mkdtemp(prefix=f"rift-{run_id}-")
    activity.logger.info("Cloning repository", repo_ref=repo_ref, path=workspace_path)
    # Actual git clone would happen here; stub for dev
    return {"workspace_path": workspace_path, "repo_ref": repo_ref}


@activity.defn
async def execute_steps(
    run_id: str,
    repo_ref: str,
    batch_spec_id: str,
    workspace_path: str,
) -> dict:
    """Execute batch spec steps in the workspace directory."""
    activity.logger.info("Executing steps", repo_ref=repo_ref, workspace=workspace_path)
    # Actual container execution would happen here; stub for dev
    return {
        "workspace_path": workspace_path,
        "repo_ref": repo_ref,
        "exit_code": 0,
    }


@activity.defn
async def capture_diff(run_id: str, repo_ref: str, workspace_path: str) -> dict:
    """Capture git diff from the workspace after step execution."""
    activity.logger.info("Capturing diff", repo_ref=repo_ref)
    # git diff HEAD would be run here; stub returns empty key
    diff_key = f"patches/{run_id}/{repo_ref.replace('/', '_')}.patch"
    return {"diff_key": diff_key, "repo_ref": repo_ref}
