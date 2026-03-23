from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class ChangesetSpecState(StrEnum):
    UNPUBLISHED = "UNPUBLISHED"
    PUBLISHING = "PUBLISHING"
    PUBLISHED = "PUBLISHED"
    MERGED = "MERGED"
    CLOSED = "CLOSED"
    ARCHIVED = "ARCHIVED"


class PublishMode(StrEnum):
    FULL_PR = "FULL_PR"
    DRAFT_PR = "DRAFT_PR"
    PUSH_ONLY = "PUSH_ONLY"


VALID_SPEC_TRANSITIONS: dict[ChangesetSpecState, set[ChangesetSpecState]] = {
    ChangesetSpecState.UNPUBLISHED: {ChangesetSpecState.PUBLISHING},
    ChangesetSpecState.PUBLISHING: {
        ChangesetSpecState.PUBLISHED,
        ChangesetSpecState.CLOSED,
    },
    ChangesetSpecState.PUBLISHED: {
        ChangesetSpecState.MERGED,
        ChangesetSpecState.CLOSED,
        ChangesetSpecState.ARCHIVED,
    },
    ChangesetSpecState.MERGED: {ChangesetSpecState.ARCHIVED},
    ChangesetSpecState.CLOSED: {ChangesetSpecState.ARCHIVED, ChangesetSpecState.PUBLISHING},
    ChangesetSpecState.ARCHIVED: set(),
}


class ChangesetSpec(BaseModel):
    id: str = Field(examples=["cs_01j2k3"])
    batch_change_id: str
    repo_ref: str
    diff_key: str
    branch: str
    title: str
    description: str = ""
    publish_mode: PublishMode = PublishMode.FULL_PR
    state: ChangesetSpecState = ChangesetSpecState.UNPUBLISHED
    external_pr_id: str | None = None
    external_pr_url: str | None = None
    spec_fingerprint: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def can_transition_to(self, new_state: ChangesetSpecState) -> bool:
        return new_state in VALID_SPEC_TRANSITIONS.get(self.state, set())


class ChangesetSpecResponse(BaseModel):
    id: str
    batch_change_id: str
    repo_ref: str
    branch: str
    title: str
    description: str
    publish_mode: PublishMode
    state: ChangesetSpecState
    external_pr_url: str | None = None
    created_at: datetime
    updated_at: datetime
