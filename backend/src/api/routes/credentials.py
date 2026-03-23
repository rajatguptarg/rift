from __future__ import annotations

from fastapi import APIRouter

from src.api.dependencies import CurrentUserDep, DBDep, NamespaceDep
from src.models.credential import CredentialCreate, CredentialResponse
from src.services.credential_service import CredentialService

router = APIRouter()


@router.get("/credentials", response_model=list[CredentialResponse])
async def list_credentials(
    db: DBDep,
    current_user: CurrentUserDep,
    namespace: NamespaceDep,
) -> list[CredentialResponse]:
    svc = CredentialService(db)
    items = await svc.list_by_namespace(namespace, current_user.id)
    return [CredentialResponse(**cred.model_dump()) for cred in items]


@router.post("/credentials", response_model=CredentialResponse, status_code=201)
async def create_credential(
    body: CredentialCreate,
    db: DBDep,
    current_user: CurrentUserDep,
) -> CredentialResponse:
    svc = CredentialService(db)
    cred = await svc.create(body, user_id=current_user.id)
    return CredentialResponse(**cred.model_dump())


@router.delete("/credentials/{credential_id}", status_code=204)
async def delete_credential(
    credential_id: str, db: DBDep, current_user: CurrentUserDep
) -> None:
    svc = CredentialService(db)
    await svc.delete(credential_id, user_id=current_user.id)
