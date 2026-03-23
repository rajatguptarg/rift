from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class CredentialScope(StrEnum):
    GLOBAL = "GLOBAL"
    ORG = "ORG"
    USER = "USER"


class Credential(BaseModel):
    id: str = Field(examples=["cred_01j2k3"])
    namespace_id: str
    user_id: str | None = None
    code_host_id: str
    scope: CredentialScope = CredentialScope.USER
    encrypted_secret: str
    kms_key_ref: str
    scopes: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    rotated_at: datetime | None = None


class CredentialCreate(BaseModel):
    namespace_id: str
    code_host_id: str
    scope: CredentialScope = CredentialScope.USER
    secret: str  # raw token — encrypted before storage
    scopes: list[str] = Field(default_factory=list)


class CredentialResponse(BaseModel):
    id: str
    namespace_id: str
    user_id: str | None = None
    code_host_id: str
    scope: CredentialScope
    scopes: list[str]
    created_at: datetime
    rotated_at: datetime | None = None
    # Never expose encrypted_secret or kms_key_ref in responses
