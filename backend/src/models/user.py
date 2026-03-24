from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class AccessRole(StrEnum):
    SUPER_USER = "SUPER_USER"
    STANDARD = "STANDARD"


class User(BaseModel):
    id: str = Field(examples=["usr_01j2k3l4m5"])
    username: str
    display_name: str
    email: str | None = None
    password_hash: str
    role: AccessRole = AccessRole.STANDARD
    auth_subject: str
    bootstrap_managed: bool = False
    last_login_at: datetime | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UserCreate(BaseModel):
    username: str
    display_name: str
    email: str | None = None
    password_hash: str
    role: AccessRole = AccessRole.STANDARD
    auth_subject: str
    bootstrap_managed: bool = False


class UserSummary(BaseModel):
    """Public-facing user summary returned in auth responses."""

    id: str
    username: str
    display_name: str
    email: str | None = None
    role: AccessRole
    bootstrap_managed: bool
    created_at: datetime


class UserResponse(BaseModel):
    id: str
    username: str
    display_name: str
    email: str | None
    role: AccessRole
    bootstrap_managed: bool
    created_at: datetime
