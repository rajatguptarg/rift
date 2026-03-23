from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class BatchRunState(StrEnum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class ExecutionStepState(StrEnum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class WorkspaceExecutionState(StrEnum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    CANCELLED = "CANCELLED"


class ExecutionStep(BaseModel):
    id: str
    workspace_execution_id: str
    step_index: int
    command: str
    state: ExecutionStepState = ExecutionStepState.PENDING
    log_key: str | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    exit_code: int | None = None


class WorkspaceExecution(BaseModel):
    id: str = Field(examples=["we_01j2k3"])
    batch_run_id: str
    repo_ref: str
    branch: str = ""
    state: WorkspaceExecutionState = WorkspaceExecutionState.PENDING
    steps: list[ExecutionStep] = Field(default_factory=list)
    diff_key: str | None = None
    log_key: str | None = None
    error_message: str | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    duration_seconds: float | None = None
    is_excluded: bool = False


class BatchRun(BaseModel):
    id: str = Field(examples=["br_01j2k3"])
    batch_change_id: str
    batch_spec_id: str
    state: BatchRunState = BatchRunState.PENDING
    total_workspaces: int = 0
    completed_workspaces: int = 0
    failed_workspaces: int = 0
    skip_errors: bool = False
    temporal_workflow_id: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: datetime | None = None
    finished_at: datetime | None = None


class BatchRunResponse(BaseModel):
    id: str
    batch_change_id: str
    batch_spec_id: str
    state: BatchRunState
    total_workspaces: int
    completed_workspaces: int
    failed_workspaces: int
    created_at: datetime
    started_at: datetime | None = None
    finished_at: datetime | None = None


class WorkspaceExecutionResponse(BaseModel):
    id: str
    batch_run_id: str
    repo_ref: str
    state: WorkspaceExecutionState
    duration_seconds: float | None = None
    error_message: str | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None
    is_excluded: bool
