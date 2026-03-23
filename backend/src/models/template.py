from __future__ import annotations

from pydantic import BaseModel, Field


class FormField(BaseModel):
    name: str
    label: str
    field_type: str = "text"  # text, textarea, select
    required: bool = True
    default: str = ""
    options: list[str] = Field(default_factory=list)  # for select type


class Template(BaseModel):
    id: str = Field(examples=["tpl_01j2k3"])
    namespace_id: str | None = None
    name: str
    description: str = ""
    category: str = "custom"
    spec_template_yaml: str
    form_schema: list[FormField] = Field(default_factory=list)
    validation_rules: dict[str, str] = Field(default_factory=dict)
    is_builtin: bool = False
    is_active: bool = True


class TemplateCreate(BaseModel):
    namespace_id: str | None = None
    name: str
    description: str = ""
    category: str = "custom"
    spec_template_yaml: str
    form_schema: list[FormField] = Field(default_factory=list)
    validation_rules: dict[str, str] = Field(default_factory=dict)


class TemplateResponse(BaseModel):
    id: str
    namespace_id: str | None = None
    name: str
    description: str
    category: str
    form_schema: list[FormField]
    validation_rules: dict[str, str]
    is_builtin: bool
    is_active: bool
