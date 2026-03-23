from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class NamespaceKind(StrEnum):
    USER = "USER"
    ORG = "ORG"


class VisibilityPolicy(BaseModel):
    default_visibility: str = "PRIVATE"
    redact_repo_names: bool = False
    redact_diffs: bool = False


class Namespace(BaseModel):
    id: str = Field(examples=["ns_01j2k3"])
    kind: NamespaceKind
    owner_user_id: str | None = None
    owner_org_id: str | None = None
    visibility_policy: VisibilityPolicy = Field(default_factory=VisibilityPolicy)


class NamespaceResponse(BaseModel):
    id: str
    kind: NamespaceKind
    owner_user_id: str | None = None
    owner_org_id: str | None = None
