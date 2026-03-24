from __future__ import annotations

import uuid
from datetime import UTC, datetime

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError

from src.adapters.mongo.user_repo import UserRepository
from src.core import logging as log_module
from src.core.config import settings
from src.models.user import AccessRole, User
from src.services.auth_service import hash_password

logger = log_module.get_logger(__name__)


class BootstrapService:
    def __init__(self, db: AsyncIOMotorDatabase) -> None:
        self._repo = UserRepository(db)

    async def seed(self) -> User | None:
        """Idempotently create the bootstrap super user if not already present."""
        # Ensure the username uniqueness index exists
        await self._repo.ensure_unique_username_index()

        existing = await self._repo.find_bootstrap_user()
        if existing is not None:
            logger.info("Bootstrap super user already exists", username=existing.username)
            return existing

        username = settings.bootstrap_superuser_username.lower()
        display_name = settings.bootstrap_superuser_display_name
        password = settings.bootstrap_superuser_password
        now = datetime.now(UTC)

        user = User(
            id=f"usr_{uuid.uuid4().hex[:12]}",
            username=username,
            display_name=display_name,
            email=None,
            password_hash=hash_password(password),
            role=AccessRole.SUPER_USER,
            auth_subject=f"local:{username}",
            bootstrap_managed=True,
            created_at=now,
            updated_at=now,
        )
        try:
            await self._repo.insert(user)
        except DuplicateKeyError:
            raced_user = await self._repo.find_by_username(username)
            if raced_user is None or not raced_user.bootstrap_managed:
                raise
            logger.info("Bootstrap super user created by another worker", username=username)
            return raced_user
        logger.info("Bootstrap super user created", username=username)
        return user
