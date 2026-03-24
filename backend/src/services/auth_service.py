from __future__ import annotations

import hashlib
import uuid
from base64 import b64encode
from datetime import UTC, datetime, timedelta

import bcrypt
from jose import jwt as jose_jwt
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.adapters.mongo.user_repo import UserRepository
from src.core.config import settings
from src.models.user import AccessRole, User, UserSummary

_PASSWORD_HASH_PREFIX = "bcrypt-sha256$"


def _prehash_password(plain: str) -> bytes:
    digest = hashlib.sha256(plain.encode("utf-8")).digest()
    return b64encode(digest)


def hash_password(plain: str) -> str:
    bcrypt_hash = bcrypt.hashpw(_prehash_password(plain), bcrypt.gensalt()).decode("utf-8")
    return f"{_PASSWORD_HASH_PREFIX}{bcrypt_hash}"


def verify_password(plain: str, hashed: str) -> bool:
    try:
        if hashed.startswith(_PASSWORD_HASH_PREFIX):
            encoded_hash = hashed.removeprefix(_PASSWORD_HASH_PREFIX).encode("utf-8")
            return bcrypt.checkpw(_prehash_password(plain), encoded_hash)
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        return False


def _issue_token(user: User) -> tuple[str, datetime]:
    """Return (access_token, expires_at)."""
    now = datetime.now(UTC)
    expires_at = now + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {
        "sub": user.id,
        "username": user.username,
        "role": user.role,
        "email": user.email or "",
        "jti": uuid.uuid4().hex,
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
    }
    token = jose_jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return token, expires_at


def to_user_summary(user: User) -> UserSummary:
    return UserSummary(
        id=user.id,
        username=user.username,
        display_name=user.display_name,
        email=user.email,
        role=user.role,
        bootstrap_managed=user.bootstrap_managed,
        created_at=user.created_at,
    )


class AuthService:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self._repo = UserRepository(db)

    async def sign_in(self, username: str, password: str) -> tuple[User, str, datetime]:
        """Authenticate user. Returns (user, access_token, expires_at) or raises ValueError."""
        user = await self._repo.find_by_username(username)
        if user is None or not verify_password(password, user.password_hash):
            raise ValueError("Invalid username or password.")
        now = datetime.now(UTC)
        await self._repo.update_last_login(user.id, now)
        token, expires_at = _issue_token(user)
        return user, token, expires_at

    async def sign_up(
        self,
        username: str,
        display_name: str,
        password: str,
        email: str | None = None,
    ) -> tuple[User, str, datetime]:
        """Create a standard user. Returns (user, access_token, expires_at) or raises ValueError."""
        normalized = username.lower()
        existing = await self._repo.find_by_username(normalized)
        if existing is not None:
            raise ValueError("Username is already in use.")
        user_id = f"usr_{uuid.uuid4().hex[:12]}"
        user = User(
            id=user_id,
            username=normalized,
            display_name=display_name.strip(),
            email=email,
            password_hash=hash_password(password),
            role=AccessRole.STANDARD,
            auth_subject=f"local:{normalized}",
            bootstrap_managed=False,
        )
        await self._repo.insert(user)
        token, expires_at = _issue_token(user)
        return user, token, expires_at
