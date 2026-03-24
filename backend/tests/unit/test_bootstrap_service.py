"""Unit tests for BootstrapService seed creation and idempotency."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pymongo.errors import DuplicateKeyError

from src.models.user import AccessRole, User
from src.services.auth_service import hash_password, verify_password


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


class TestBootstrapService:
    @pytest.fixture
    def mock_db(self):
        return MagicMock()

    @pytest.mark.asyncio
    async def test_seed_creates_super_user_when_none_exists(self, mock_db):
        from src.services.bootstrap_service import BootstrapService
        svc = BootstrapService(mock_db)
        svc._repo = AsyncMock()
        svc._repo.ensure_unique_username_index.return_value = None
        svc._repo.find_bootstrap_user.return_value = None
        svc._repo.insert.return_value = None

        result = await svc.seed()
        assert result is not None
        assert result.role == AccessRole.SUPER_USER
        assert result.bootstrap_managed is True
        svc._repo.insert.assert_called_once()

    @pytest.mark.asyncio
    async def test_seed_is_idempotent_when_bootstrap_user_exists(self, mock_db):
        from src.services.bootstrap_service import BootstrapService
        existing = make_bootstrap_user()
        svc = BootstrapService(mock_db)
        svc._repo = AsyncMock()
        svc._repo.ensure_unique_username_index.return_value = None
        svc._repo.find_bootstrap_user.return_value = existing

        result = await svc.seed()
        assert result is not None
        assert result.id == existing.id
        # Should NOT insert a new user
        svc._repo.insert.assert_not_called()

    @pytest.mark.asyncio
    async def test_seed_uses_env_settings(self, mock_db):
        from src.services.bootstrap_service import BootstrapService
        svc = BootstrapService(mock_db)
        svc._repo = AsyncMock()
        svc._repo.ensure_unique_username_index.return_value = None
        svc._repo.find_bootstrap_user.return_value = None
        svc._repo.insert.return_value = None

        with patch("src.services.bootstrap_service.settings") as mock_settings:
            mock_settings.bootstrap_superuser_username = "admin"
            mock_settings.bootstrap_superuser_password = "adminpass"
            mock_settings.bootstrap_superuser_display_name = "Admin User"
            result = await svc.seed()

        assert result is not None
        assert result.username == "admin"
        assert result.display_name == "Admin User"

    @pytest.mark.asyncio
    async def test_seed_hashes_long_bootstrap_password(self, mock_db):
        from src.services.bootstrap_service import BootstrapService
        svc = BootstrapService(mock_db)
        svc._repo = AsyncMock()
        svc._repo.ensure_unique_username_index.return_value = None
        svc._repo.find_bootstrap_user.return_value = None
        svc._repo.insert.return_value = None
        long_password = "bootstrap-" * 12

        with patch("src.services.bootstrap_service.settings") as mock_settings:
            mock_settings.bootstrap_superuser_username = "admin"
            mock_settings.bootstrap_superuser_password = long_password
            mock_settings.bootstrap_superuser_display_name = "Admin User"
            result = await svc.seed()

        assert result is not None
        assert verify_password(long_password, result.password_hash)

    @pytest.mark.asyncio
    async def test_seed_recovers_from_duplicate_key_race(self, mock_db):
        from src.services.bootstrap_service import BootstrapService

        existing = make_bootstrap_user()
        svc = BootstrapService(mock_db)
        svc._repo = AsyncMock()
        svc._repo.ensure_unique_username_index.return_value = None
        svc._repo.find_bootstrap_user.return_value = None
        svc._repo.insert.side_effect = DuplicateKeyError("duplicate bootstrap user")
        svc._repo.find_by_username.return_value = existing

        result = await svc.seed()

        assert result is not None
        assert result.id == existing.id
        svc._repo.find_by_username.assert_awaited_once_with("master")
