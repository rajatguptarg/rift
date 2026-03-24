from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.api.dependencies import CurrentUserDep, DBDep
from src.models.audit import AuditAction
from src.models.user import UserSummary
from src.services.audit_service import AuditService
from src.services.auth_service import AuthService, to_user_summary

router = APIRouter(prefix="/auth", tags=["auth"])


class SignInRequest(BaseModel):
    username: str
    password: str = Field(min_length=1)


class SignUpRequest(BaseModel):
    username: str = Field(min_length=3, max_length=32, pattern=r"^[a-z0-9._-]+$")
    display_name: str = Field(min_length=1, max_length=80)
    email: str | None = None
    password: str = Field(min_length=6, max_length=72)


class AuthSessionResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_at: datetime
    user: UserSummary


class CurrentUserResponse(BaseModel):
    user: UserSummary


@router.post("/sign-in", response_model=AuthSessionResponse)
async def sign_in(body: SignInRequest, db: DBDep) -> AuthSessionResponse:
    svc = AuthService(db)
    try:
        user, token, expires_at = await svc.sign_in(body.username, body.password)
    except ValueError as exc:
        raise HTTPException(
            status_code=401,
            detail={
                "code": "AUTHENTICATION_REQUIRED",
                "message": str(exc),
                "details": {},
            },
        ) from exc

    # Record audit event
    audit = AuditService(db)
    await audit.record(
        actor_id=user.id,
        resource_type="user",
        resource_id=user.id,
        action=AuditAction.LOGIN,
        payload={"username": user.username},
    )

    return AuthSessionResponse(
        access_token=token,
        token_type="Bearer",
        expires_at=expires_at,
        user=to_user_summary(user),
    )


@router.post("/sign-up", response_model=AuthSessionResponse, status_code=201)
async def sign_up(body: SignUpRequest, db: DBDep) -> AuthSessionResponse:
    svc = AuthService(db)
    try:
        user, token, expires_at = await svc.sign_up(
            username=body.username,
            display_name=body.display_name,
            password=body.password,
            email=body.email,
        )
    except ValueError as exc:
        msg = str(exc)
        if "already in use" in msg:
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "USERNAME_CONFLICT",
                    "message": msg,
                    "details": {"field": "username"},
                },
            ) from exc
        raise HTTPException(
            status_code=400,
            detail={"code": "VALIDATION_ERROR", "message": msg, "details": {}},
        ) from exc

    return AuthSessionResponse(
        access_token=token,
        token_type="Bearer",
        expires_at=expires_at,
        user=to_user_summary(user),
    )


@router.get("/me", response_model=CurrentUserResponse)
async def get_current_user_info(current_user: CurrentUserDep) -> CurrentUserResponse:
    return CurrentUserResponse(user=to_user_summary(current_user))
