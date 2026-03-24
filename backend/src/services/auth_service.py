from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from jose import jwt as jose_jwt
from motor.motor_asyncio import AsyncIOMotorDatabase
from passlib.context import CryptContext

from src.adapters.mongo.user_repo import UserRepository
from src.core.config import settings
from src.models.user import AccessRole, User, UserSummary

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return _pwd_context.verify(plain, hashed)


def _issue_token(user: User) -> tuple[str, datetime]:
    """Return (access_token, expires_at)."""
    now = datetime.now(timezone.utc)
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
        now = datetime.now(timezone.utc)
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
