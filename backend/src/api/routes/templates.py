from __future__ import annotations

from fastapi import APIRouter

from src.api.dependencies import CurrentUserDep, DBDep, NamespaceDep
from src.models.template import TemplateCreate, TemplateResponse
from src.services.template_service import TemplateService

router = APIRouter()


@router.get("/templates", response_model=list[TemplateResponse])
async def list_templates(
    db: DBDep,
    current_user: CurrentUserDep,
    namespace: NamespaceDep,
) -> list[TemplateResponse]:
    svc = TemplateService(db)
    items = await svc.list_available(namespace_id=namespace)
    return [TemplateResponse(**tpl.model_dump()) for tpl in items]


@router.post("/templates", response_model=TemplateResponse, status_code=201)
async def create_template(
    body: TemplateCreate,
    db: DBDep,
    current_user: CurrentUserDep,
) -> TemplateResponse:
    svc = TemplateService(db)
    tpl = await svc.create(body)
    return TemplateResponse(**tpl.model_dump())


@router.post("/templates/{template_id}/generate", response_model=dict)
async def generate_spec_from_template(
    template_id: str,
    body: dict,
    db: DBDep,
    current_user: CurrentUserDep,
) -> dict:
    svc = TemplateService(db)
    spec_yaml = await svc.generate_spec(template_id, params=body.get("params", {}))
    return {"spec_yaml": spec_yaml}
