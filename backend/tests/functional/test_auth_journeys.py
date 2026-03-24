"""Functional tests for clean-environment bootstrap login journey."""
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
async def test_bootstrap_admin_can_sign_in_on_clean_environment():
    """
    Simulates a clean startup: bootstrap seeding runs, then master/master works.
    """
    from src.services.bootstrap_service import BootstrapService
    from src.services.auth_service import AuthService

    mock_db = MagicMock()

    # 1. Bootstrap seeding
    bootstrap_svc = BootstrapService(mock_db)
    bootstrap_svc._repo = AsyncMock()
    bootstrap_svc._repo.ensure_unique_username_index.return_value = None
    bootstrap_svc._repo.find_bootstrap_user.return_value = None
    bootstrap_svc._repo.insert.return_value = None
    seeded_user = await bootstrap_svc.seed()
    assert seeded_user is not None
    assert seeded_user.role == AccessRole.SUPER_USER

    # 2. Auth sign-in with master/master
    auth_svc = AuthService(mock_db)
    auth_svc._repo = AsyncMock()
    auth_svc._repo.find_by_username.return_value = seeded_user
    auth_svc._repo.update_last_login.return_value = None

    user, token, _ = await auth_svc.sign_in(
        seeded_user.username, "master"
    )
    assert user.role == AccessRole.SUPER_USER
    assert isinstance(token, str)


@pytest.mark.asyncio
async def test_bootstrap_does_not_duplicate_on_restart():
    """Verifies idempotency: second startup must not create a second super user."""
    from src.services.bootstrap_service import BootstrapService
    existing = make_bootstrap_user()
    mock_db = MagicMock()
    svc = BootstrapService(mock_db)
    svc._repo = AsyncMock()
    svc._repo.ensure_unique_username_index.return_value = None
    svc._repo.find_bootstrap_user.return_value = existing

    result = await svc.seed()
    assert result.id == existing.id
    svc._repo.insert.assert_not_called()
