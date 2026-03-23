from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class User(BaseModel):
    id: str = Field(examples=["usr_01j2k3l4m5"])
    email: str
    display_name: str
    auth_subject: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserCreate(BaseModel):
    email: str
    display_name: str
    auth_subject: str


class UserResponse(BaseModel):
    id: str
    email: str
    display_name: str
    created_at: datetime
