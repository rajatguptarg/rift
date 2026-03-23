from __future__ import annotations

import re
import uuid

from motor.motor_asyncio import AsyncIOMotorDatabase

from src.adapters.mongo.base_repository import BaseRepository
from src.core.errors import ValidationError
from src.models.template import Template, TemplateCreate


class _TemplateRepository(BaseRepository[Template]):
    collection_name = "templates"
    model_class = Template


class TemplateService:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self._repo = _TemplateRepository(db)

    async def create(self, data: TemplateCreate) -> Template:
        tpl = Template(
            id=f"tpl_{uuid.uuid4().hex[:12]}",
            **data.model_dump(),
        )
        return await self._repo.insert(tpl)

    async def list_available(self, namespace_id: str | None = None) -> list[Template]:
        """Return global built-ins plus namespace-scoped templates."""
        filter_: dict = {
            "$or": [
                {"is_builtin": True},
                {"namespace_id": namespace_id} if namespace_id else {},
            ],
            "is_active": True,
        }
        return await self._repo.find_many(filter_, limit=100)

    async def generate_spec(
        self, template_id: str, params: dict[str, str]
    ) -> str:
        """Validate parameters against rules and substitute into template YAML."""
        tpl = await self._repo.get_by_id(template_id)

        # Validate each field against regex rules
        errors: dict[str, str] = {}
        for field in tpl.form_schema:
            value = params.get(field.name, field.default)
            if field.required and not value:
                errors[field.name] = "This field is required."
                continue
            rule = tpl.validation_rules.get(field.name)
            if rule and value and not re.fullmatch(rule, value):
                errors[field.name] = f"Value does not match pattern: {rule}"

        if errors:
            raise ValidationError("Template parameter validation failed", details=errors)

        # Simple string substitution: {{field_name}} → value
        spec_yaml = tpl.spec_template_yaml
        for key, value in params.items():
            spec_yaml = spec_yaml.replace(f"{{{{{key}}}}}", value)

        return spec_yaml
