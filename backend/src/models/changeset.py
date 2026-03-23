from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class ChangesetState(StrEnum):
    UNPUBLISHED = "UNPUBLISHED"
    OPEN = "OPEN"
    DRAFT = "DRAFT"
    MERGED = "MERGED"
    CLOSED = "CLOSED"
    ARCHIVED = "ARCHIVED"


class ReviewDecision(StrEnum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    CHANGES_REQUESTED = "CHANGES_REQUESTED"


class CIState(StrEnum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    PASSED = "PASSED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


class Changeset(BaseModel):
    id: str = Field(examples=["ch_01j2k3"])
    changeset_spec_id: str
    batch_change_id: str
    repo_ref: str
    external_id: str | None = None
    external_url: str | None = None
    state: ChangesetState = ChangesetState.UNPUBLISHED
    title: str
    branch: str
    review_state: ReviewDecision = ReviewDecision.PENDING
    ci_state: CIState = CIState.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    merged_at: datetime | None = None
    closed_at: datetime | None = None


class ChangesetEvent(BaseModel):
    id: str
    changeset_id: str
    event_type: str
    payload: dict = Field(default_factory=dict)
    occurred_at: datetime = Field(default_factory=datetime.utcnow)


class ChangesetResponse(BaseModel):
    id: str
    changeset_spec_id: str
    batch_change_id: str
    repo_ref: str
    external_url: str | None = None
    state: ChangesetState
    title: str
    branch: str
    review_state: ReviewDecision
    ci_state: CIState
    created_at: datetime
    updated_at: datetime
    merged_at: datetime | None = None
