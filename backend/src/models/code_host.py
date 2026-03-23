from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class CodeHostKind(StrEnum):
    GITHUB = "GITHUB"
    GITLAB = "GITLAB"
    BITBUCKET_SERVER = "BITBUCKET_SERVER"
    BITBUCKET_CLOUD = "BITBUCKET_CLOUD"
    GERRIT = "GERRIT"


class CodeHost(BaseModel):
    id: str = Field(examples=["ch_01j2k3"])
    kind: CodeHostKind
    base_url: str
    display_name: str
    is_active: bool = True


class CodeHostCreate(BaseModel):
    kind: CodeHostKind
    base_url: str
    display_name: str


class CodeHostResponse(BaseModel):
    id: str
    kind: CodeHostKind
    base_url: str
    display_name: str
    is_active: bool
