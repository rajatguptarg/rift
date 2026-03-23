from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class Organization(BaseModel):
    id: str = Field(examples=["org_01j2k3l4"])
    name: str
    slug: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class OrganizationCreate(BaseModel):
    name: str
    slug: str


class OrganizationResponse(BaseModel):
    id: str
    name: str
    slug: str
    created_at: datetime
