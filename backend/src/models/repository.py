from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from src.models.common import Visibility


class Repository(BaseModel):
    id: str = Field(examples=["repo_01j2k3"])
    external_repo_ref: str
    code_host_id: str
    name: str
    default_branch: str = "main"
    mirror_ref: str | None = None
    visibility: Visibility = Visibility.PRIVATE
    last_synced_at: datetime | None = None


class RepositoryResponse(BaseModel):
    id: str
    external_repo_ref: str
    code_host_id: str
    name: str
    default_branch: str
    visibility: Visibility
    last_synced_at: datetime | None = None
