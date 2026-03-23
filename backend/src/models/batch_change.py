from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class BatchChangeState(StrEnum):
    DRAFT = "DRAFT"
    PREVIEW_RUNNING = "PREVIEW_RUNNING"
    PREVIEW_READY = "PREVIEW_READY"
    APPLYING = "APPLYING"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    ARCHIVED = "ARCHIVED"
    FAILED = "FAILED"


# Valid state transitions
VALID_TRANSITIONS: dict[BatchChangeState, set[BatchChangeState]] = {
    BatchChangeState.DRAFT: {BatchChangeState.PREVIEW_RUNNING, BatchChangeState.ARCHIVED},
    BatchChangeState.PREVIEW_RUNNING: {BatchChangeState.PREVIEW_READY, BatchChangeState.FAILED},
    BatchChangeState.PREVIEW_READY: {
        BatchChangeState.APPLYING,
        BatchChangeState.PREVIEW_RUNNING,  # re-run after spec edit
        BatchChangeState.ARCHIVED,
    },
    BatchChangeState.APPLYING: {BatchChangeState.ACTIVE, BatchChangeState.FAILED},
    BatchChangeState.ACTIVE: {
        BatchChangeState.PAUSED,
        BatchChangeState.ARCHIVED,
        BatchChangeState.PREVIEW_RUNNING,  # spec re-run
    },
    BatchChangeState.PAUSED: {BatchChangeState.ACTIVE, BatchChangeState.ARCHIVED},
    BatchChangeState.FAILED: {BatchChangeState.PREVIEW_RUNNING, BatchChangeState.ARCHIVED},
    BatchChangeState.ARCHIVED: set(),
}


class SourceMode(StrEnum):
    UI = "UI"
    CLI = "CLI"


class BatchChange(BaseModel):
    id: str = Field(examples=["bc_01j2k3"])
    namespace_id: str
    name: str
    description: str = ""
    source_mode: SourceMode = SourceMode.UI
    state: BatchChangeState = BatchChangeState.DRAFT
    created_by: str
    active_spec_id: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    archived_at: datetime | None = None
    version: int = 0

    def can_transition_to(self, new_state: BatchChangeState) -> bool:
        return new_state in VALID_TRANSITIONS.get(self.state, set())


class BatchChangeCreate(BaseModel):
    namespace_id: str
    name: str
    description: str = ""
    source_mode: SourceMode = SourceMode.UI


class BatchChangeResponse(BaseModel):
    id: str
    namespace_id: str
    name: str
    description: str
    source_mode: SourceMode
    state: BatchChangeState
    created_by: str
    active_spec_id: str | None = None
    created_at: datetime
    updated_at: datetime
    archived_at: datetime | None = None
    version: int
