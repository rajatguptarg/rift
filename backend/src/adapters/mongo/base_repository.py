from __future__ import annotations

from typing import Any, TypeVar

from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase
from pydantic import BaseModel

from src.core.errors import NotFoundError, OptimisticLockError

T = TypeVar("T", bound=BaseModel)


class BaseRepository[T: BaseModel]:
    """
    Generic MongoDB repository providing optimistic concurrency via a `version`
    field. Subclasses declare `collection_name` and `model_class`.
    """

    collection_name: str
    model_class: type[T]

    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self._collection: AsyncIOMotorCollection = db[self.collection_name]

    # ── Internal helpers ─────────────────────────────────────────────────────

    def _to_doc(self, model: T) -> dict[str, Any]:
        doc = model.model_dump()
        doc["_id"] = doc.pop("id", None)
        return doc

    def _from_doc(self, doc: dict[str, Any]) -> T:
        doc["id"] = str(doc.pop("_id"))
        return self.model_class.model_validate(doc)

    # ── CRUD ─────────────────────────────────────────────────────────────────

    async def insert(self, entity: T) -> T:
        doc = self._to_doc(entity)
        await self._collection.insert_one(doc)
        return entity

    async def find_by_id(self, entity_id: str) -> T | None:
        doc = await self._collection.find_one({"_id": entity_id})
        if doc is None:
            return None
        return self._from_doc(doc)

    async def get_by_id(self, entity_id: str) -> T:
        entity = await self.find_by_id(entity_id)
        if entity is None:
            raise NotFoundError(
                f"{self.model_class.__name__} '{entity_id}' not found"
            )
        return entity

    async def update_with_version(
        self,
        entity_id: str,
        expected_version: int,
        update_fields: dict[str, Any],
    ) -> T:
        """Atomic update guarded by optimistic concurrency version check."""
        new_version = expected_version + 1
        result = await self._collection.find_one_and_update(
            {"_id": entity_id, "version": expected_version},
            {"$set": {**update_fields, "version": new_version}},
            return_document=True,
        )
        if result is None:
            raise OptimisticLockError(self.model_class.__name__, expected_version)
        return self._from_doc(result)

    async def delete(self, entity_id: str) -> None:
        await self._collection.delete_one({"_id": entity_id})

    async def find_many(
        self,
        filter_: dict[str, Any],
        skip: int = 0,
        limit: int = 25,
        sort: list[tuple[str, int]] | None = None,
    ) -> list[T]:
        cursor = self._collection.find(filter_)
        if sort:
            cursor = cursor.sort(sort)
        cursor = cursor.skip(skip).limit(limit)
        return [self._from_doc(doc) async for doc in cursor]

    async def count(self, filter_: dict[str, Any]) -> int:
        return await self._collection.count_documents(filter_)
