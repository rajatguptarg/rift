from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class AuditAction(StrEnum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    STATE_TRANSITION = "STATE_TRANSITION"
    PUBLISH = "PUBLISH"
    LOGIN = "LOGIN"


class AuditEvent(BaseModel):
    id: str = Field(examples=["ae_01j2k3"])
    actor_id: str
    resource_type: str
    resource_id: str
    action: AuditAction
    payload: dict = Field(default_factory=dict)
    occurred_at: datetime = Field(default_factory=datetime.utcnow)


class AuditEventResponse(BaseModel):
    id: str
    actor_id: str
    resource_type: str
    resource_id: str
    action: AuditAction
    payload: dict
    occurred_at: datetime
