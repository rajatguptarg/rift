from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Generic, TypeVar

from pydantic import BaseModel, Field


T = TypeVar("T")


# ── Pagination ──────────────────────────────────────────────────────────────

class CursorPage(BaseModel, Generic[T]):
    items: list[T]
    next_cursor: str | None = None
    total: int | None = None


class PageParams(BaseModel):
    cursor: str | None = None
    limit: int = Field(default=25, ge=1, le=100)


# ── Error Response ───────────────────────────────────────────────────────────

class ErrorDetail(BaseModel):
    code: str
    message: str
    details: dict = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    error: ErrorDetail


# ── Common Enums ─────────────────────────────────────────────────────────────

class SortOrder(StrEnum):
    ASC = "asc"
    DESC = "desc"


class Visibility(StrEnum):
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"


# ── Timestamps mixin ─────────────────────────────────────────────────────────

class TimestampedModel(BaseModel):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
