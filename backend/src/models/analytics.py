from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field


class BatchChangeStats(BaseModel):
    batch_change_id: str
    total: int = 0
    unpublished: int = 0
    open: int = 0
    draft: int = 0
    merged: int = 0
    closed: int = 0
    archived: int = 0
    ci_passed: int = 0
    ci_failed: int = 0
    review_approved: int = 0
    computed_at: datetime = Field(default_factory=datetime.utcnow)


class BurndownDaily(BaseModel):
    batch_change_id: str
    date: date
    total: int
    merged: int
    closed: int
    open: int


class BurndownResponse(BaseModel):
    batch_change_id: str
    data: list[BurndownDaily]


class StatsResponse(BaseModel):
    batch_change_id: str
    total: int
    unpublished: int
    open: int
    draft: int
    merged: int
    closed: int
    archived: int
    ci_passed: int
    ci_failed: int
    review_approved: int
