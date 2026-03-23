from __future__ import annotations

import uuid

from motor.motor_asyncio import AsyncIOMotorDatabase

from src.adapters.mongo.base_repository import BaseRepository
from src.core.encryption import decrypt_secret, encrypt_secret
from src.core.errors import NotFoundError
from src.core.logging import get_logger
from src.models.credential import Credential, CredentialCreate, CredentialScope

logger = get_logger(__name__)


class _CredentialRepository(BaseRepository[Credential]):
    collection_name = "credentials"
    model_class = Credential


class CredentialService:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self._repo = _CredentialRepository(db)

    async def create(
        self, data: CredentialCreate, user_id: str
    ) -> Credential:
        encrypted, kms_ref = encrypt_secret(data.secret)
        cred = Credential(
            id=f"cred_{uuid.uuid4().hex[:12]}",
            namespace_id=data.namespace_id,
            user_id=user_id if data.scope == CredentialScope.USER else None,
            code_host_id=data.code_host_id,
            scope=data.scope,
            encrypted_secret=encrypted,
            kms_key_ref=kms_ref,
            scopes=data.scopes,
        )
        return await self._repo.insert(cred)

    async def list_by_namespace(
        self, namespace_id: str, user_id: str
    ) -> list[Credential]:
        """Return global + org + user credentials visible to the caller."""
        return await self._repo.find_many(
            {
                "$or": [
                    {"namespace_id": namespace_id, "scope": CredentialScope.GLOBAL},
                    {"namespace_id": namespace_id, "scope": CredentialScope.ORG},
                    {"namespace_id": namespace_id, "user_id": user_id},
                ]
            },
            limit=100,
        )

    async def delete(self, credential_id: str, user_id: str) -> None:
        cred = await self._repo.get_by_id(credential_id)
        # Only allow deletion by owner or admins (simplified: owner only)
        if cred.user_id and cred.user_id != user_id and cred.scope == CredentialScope.USER:
            from src.core.errors import AuthorizationError
            raise AuthorizationError("You do not own this credential.")
        await self._repo.delete(credential_id)
        logger.info("Credential deleted", id=credential_id)

    async def resolve_for_namespace(
        self, namespace_id: str, code_host_id: str, user_id: str
    ) -> Credential | None:
        """Scope resolution: user > org > global."""
        for scope in [CredentialScope.USER, CredentialScope.ORG, CredentialScope.GLOBAL]:
            filter_ = {
                "namespace_id": namespace_id,
                "code_host_id": code_host_id,
                "scope": scope,
            }
            if scope == CredentialScope.USER:
                filter_["user_id"] = user_id
            docs = await self._repo.find_many(filter_, limit=1)
            if docs:
                return docs[0]
        return None
