"""Integration tests for auth API routes using an in-memory FastAPI test client."""
from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient, ASGITransport

from src.models.user import AccessRole, User
from src.services.auth_service import hash_password


def make_user(username="alice", role=AccessRole.STANDARD, bootstrap_managed=False) -> User:
    return User(
        id=f"usr_{username}001",
        username=username,
        display_name=username.title(),
        email=None,
        password_hash=hash_password("secret123"),
        role=role,
        auth_subject=f"local:{username}",
        bootstrap_managed=bootstrap_managed,
    )


@pytest.fixture
def app():
    from src.main import create_app
    return create_app()


@pytest.mark.asyncio
async def test_sign_in_success(app):
    alice = make_user("alice")
    mock_repo = AsyncMock()
    mock_repo.find_by_username.return_value = alice
    mock_repo.update_last_login.return_value = None
    mock_audit_repo = AsyncMock()
    mock_audit_repo.insert.return_value = MagicMock()

    with (
        patch("src.services.auth_service.UserRepository", return_value=mock_repo),
        patch("src.services.audit_service._AuditRepository", return_value=mock_audit_repo),
        patch("src.adapters.mongo.client.get_database", return_value=MagicMock()),
        patch("src.adapters.redis.client.get_redis", return_value=AsyncMock()),
    ):
        transport = ASGITransport(app=app)  # type: ignore[arg-type]
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.post("/api/v1/auth/sign-in", json={"username": "alice", "password": "secret123"})

    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "Bearer"
    assert data["user"]["username"] == "alice"


@pytest.mark.asyncio
async def test_sign_in_invalid_credentials(app):
    mock_repo = AsyncMock()
    mock_repo.find_by_username.return_value = None

    with (
        patch("src.services.auth_service.UserRepository", return_value=mock_repo),
        patch("src.adapters.mongo.client.get_database", return_value=MagicMock()),
        patch("src.adapters.redis.client.get_redis", return_value=AsyncMock()),
    ):
        transport = ASGITransport(app=app)  # type: ignore[arg-type]
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.post("/api/v1/auth/sign-in", json={"username": "ghost", "password": "wrong"})

    assert res.status_code == 401


@pytest.mark.asyncio
async def test_sign_up_success(app):
    mock_repo = AsyncMock()
    mock_repo.find_by_username.return_value = None
    mock_repo.insert.return_value = None

    with (
        patch("src.services.auth_service.UserRepository", return_value=mock_repo),
        patch("src.adapters.mongo.client.get_database", return_value=MagicMock()),
        patch("src.adapters.redis.client.get_redis", return_value=AsyncMock()),
    ):
        transport = ASGITransport(app=app)  # type: ignore[arg-type]
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.post(
                "/api/v1/auth/sign-up",
                json={"username": "newuser", "display_name": "New User", "password": "pass1234"},
            )

    assert res.status_code == 201
    data = res.json()
    assert data["user"]["username"] == "newuser"
    assert data["user"]["role"] == "STANDARD"


@pytest.mark.asyncio
async def test_sign_up_duplicate_username(app):
    existing = make_user("taken")
    mock_repo = AsyncMock()
    mock_repo.find_by_username.return_value = existing

    with (
        patch("src.services.auth_service.UserRepository", return_value=mock_repo),
        patch("src.adapters.mongo.client.get_database", return_value=MagicMock()),
        patch("src.adapters.redis.client.get_redis", return_value=AsyncMock()),
    ):
        transport = ASGITransport(app=app)  # type: ignore[arg-type]
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            res = await client.post(
                "/api/v1/auth/sign-up",
                json={"username": "taken", "display_name": "Taken", "password": "pass1234"},
            )

    assert res.status_code == 409
