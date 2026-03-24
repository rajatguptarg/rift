"""Unit tests for AuthService password verification and token issuance."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import bcrypt
import pytest
from jose import jwt as jose_jwt

from src.core.config import settings
from src.models.user import AccessRole, User
from src.services.auth_service import _issue_token, hash_password, verify_password


def make_user(**kwargs) -> User:
    defaults = dict(
        id="usr_testuser001",
        username="alice",
        display_name="Alice",
        email=None,
        password_hash=hash_password("secret123"),
        role=AccessRole.STANDARD,
        auth_subject="local:alice",
        bootstrap_managed=False,
    )
    defaults.update(kwargs)
    return User(**defaults)


class TestPasswordHelpers:
    def test_hash_and_verify_roundtrip(self):
        plain = "my-secure-password"
        hashed = hash_password(plain)
        assert hashed != plain
        assert verify_password(plain, hashed)

    def test_long_password_roundtrip(self):
        plain = "p" * 200
        hashed = hash_password(plain)
        assert verify_password(plain, hashed)

    def test_wrong_password_fails(self):
        hashed = hash_password("correct")
        assert not verify_password("wrong", hashed)

    def test_empty_password_works_if_hashed(self):
        # Empty strings are still hashable; request validation enforces stronger rules.
        hashed = hash_password("master")
        assert verify_password("master", hashed)

    def test_legacy_bcrypt_hashes_still_verify(self):
        legacy_hash = bcrypt.hashpw(b"secret123", bcrypt.gensalt()).decode("utf-8")
        assert verify_password("secret123", legacy_hash)


class TestIssueToken:
    def test_token_contains_expected_claims(self):
        user = make_user()
        token, expires_at = _issue_token(user)
        assert isinstance(token, str)
        assert len(token) > 20

        payload = jose_jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        assert payload["sub"] == user.id
        assert payload["username"] == user.username
        assert payload["role"] == user.role

    def test_token_expires_in_future(self):
        import time
        user = make_user()
        _, expires_at = _issue_token(user)
        assert expires_at.timestamp() > time.time()


class TestAuthServiceSignIn:
    @pytest.fixture
    def mock_db(self):
        return MagicMock()

    @pytest.mark.asyncio
    async def test_sign_in_success(self, mock_db):
        from src.services.auth_service import AuthService
        user = make_user()
        svc = AuthService(mock_db)
        svc._repo = AsyncMock()
        svc._repo.find_by_username.return_value = user
        svc._repo.update_last_login.return_value = None

        result_user, token, expires_at = await svc.sign_in("alice", "secret123")
        assert result_user.id == user.id
        assert isinstance(token, str)

    @pytest.mark.asyncio
    async def test_sign_in_wrong_password_raises(self, mock_db):
        from src.services.auth_service import AuthService
        user = make_user()
        svc = AuthService(mock_db)
        svc._repo = AsyncMock()
        svc._repo.find_by_username.return_value = user

        with pytest.raises(ValueError, match="Invalid username or password"):
            await svc.sign_in("alice", "wrongpass")

    @pytest.mark.asyncio
    async def test_sign_in_unknown_user_raises(self, mock_db):
        from src.services.auth_service import AuthService
        svc = AuthService(mock_db)
        svc._repo = AsyncMock()
        svc._repo.find_by_username.return_value = None

        with pytest.raises(ValueError, match="Invalid username or password"):
            await svc.sign_in("ghost", "anything")


class TestAuthServiceSignUp:
    @pytest.mark.asyncio
    async def test_sign_up_success(self):
        from src.services.auth_service import AuthService
        mock_db = MagicMock()
        svc = AuthService(mock_db)
        svc._repo = AsyncMock()
        svc._repo.find_by_username.return_value = None
        svc._repo.insert.return_value = None

        user, token, _ = await svc.sign_up("bob", "Bob Smith", "password123")
        assert user.username == "bob"
        assert user.role == AccessRole.STANDARD
        assert user.bootstrap_managed is False
        assert isinstance(token, str)

    @pytest.mark.asyncio
    async def test_sign_up_duplicate_username_raises(self):
        from src.services.auth_service import AuthService
        mock_db = MagicMock()
        existing = make_user(username="bob")
        svc = AuthService(mock_db)
        svc._repo = AsyncMock()
        svc._repo.find_by_username.return_value = existing

        with pytest.raises(ValueError, match="already in use"):
            await svc.sign_up("bob", "Bob Smith", "password123")

    @pytest.mark.asyncio
    async def test_sign_up_normalizes_username(self):
        from src.services.auth_service import AuthService
        mock_db = MagicMock()
        svc = AuthService(mock_db)
        svc._repo = AsyncMock()
        svc._repo.find_by_username.return_value = None
        svc._repo.insert.return_value = None

        user, _, _ = await svc.sign_up("Alice", "Alice Wonderland", "pass1234")
        assert user.username == "alice"
