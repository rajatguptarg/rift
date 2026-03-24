"""Integration tests for bootstrap super-user idempotency and role resolution."""
from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.models.user import AccessRole, User
from src.services.auth_service import hash_password


def make_bootstrap_user() -> User:
    return User(
        id="usr_bootstrap001",
        username="master",
        display_name="Rift Master",
        email=None,
        password_hash=hash_password("master"),
        role=AccessRole.SUPER_USER,
        auth_subject="local:master",
        bootstrap_managed=True,
    )


@pytest.mark.asyncio
async def test_bootstrap_seed_creates_super_user():
    from src.services.bootstrap_service import BootstrapService
    mock_db = MagicMock()
    svc = BootstrapService(mock_db)
    svc._repo = AsyncMock()
    svc._repo.ensure_unique_username_index.return_value = None
    svc._repo.find_bootstrap_user.return_value = None
    svc._repo.insert.return_value = None

    user = await svc.seed()
    assert user is not None
    assert user.role == AccessRole.SUPER_USER
    assert user.bootstrap_managed is True
    svc._repo.insert.assert_called_once()


@pytest.mark.asyncio
async def test_bootstrap_seed_idempotent_on_restart():
    from src.services.bootstrap_service import BootstrapService
    existing = make_bootstrap_user()
    mock_db = MagicMock()
    svc = BootstrapService(mock_db)
    svc._repo = AsyncMock()
    svc._repo.ensure_unique_username_index.return_value = None
    svc._repo.find_bootstrap_user.return_value = existing

    # Call seed twice — should not insert
    await svc.seed()
    await svc.seed()
    svc._repo.insert.assert_not_called()


@pytest.mark.asyncio
async def test_bootstrap_user_can_sign_in():
    from src.services.auth_service import AuthService
    bootstrap = make_bootstrap_user()
    mock_db = MagicMock()
    svc = AuthService(mock_db)
    svc._repo = AsyncMock()
    svc._repo.find_by_username.return_value = bootstrap
    svc._repo.update_last_login.return_value = None

    user, token, _ = await svc.sign_in("master", "master")
    assert user.role == AccessRole.SUPER_USER
    assert isinstance(token, str)
