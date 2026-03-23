from __future__ import annotations

import hashlib
from datetime import datetime

from pydantic import BaseModel, Field


class BatchSpec(BaseModel):
    id: str = Field(examples=["bs_01j2k3"])
    batch_change_id: str
    spec_yaml: str
    spec_hash: str = ""  # SHA-256 computed on creation
    template_bindings: dict[str, str] | None = None
    search_query: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)

    def model_post_init(self, __context: object) -> None:
        if not self.spec_hash:
            self.spec_hash = hashlib.sha256(self.spec_yaml.encode()).hexdigest()


class BatchSpecCreate(BaseModel):
    batch_change_id: str
    spec_yaml: str
    template_bindings: dict[str, str] | None = None


class BatchSpecResponse(BaseModel):
    id: str
    batch_change_id: str
    spec_yaml: str
    spec_hash: str
    search_query: str
    created_at: datetime
