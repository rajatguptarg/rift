"""Integration test fixtures — skips suite if required services are unreachable."""

from __future__ import annotations

import socket

import pytest
import requests


SEAWEEDFS_S3_ENDPOINT = "http://localhost:9000"

MONGODB_TEST_URL = "mongodb://localhost:27017"
MONGODB_TEST_DB = "rift_test"


def _is_seaweedfs_reachable() -> bool:
    try:
        requests.head(SEAWEEDFS_S3_ENDPOINT, timeout=3)
        return True
    except requests.exceptions.ConnectionError:
        return False


def _is_mongodb_reachable() -> bool:
    try:
        socket.setdefaulttimeout(3)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("localhost", 27017))
        return True
    except (socket.error, OSError):
        return False


@pytest.fixture(scope="session", autouse=True)
def require_seaweedfs() -> None:
    """Skip the entire integration suite if SeaweedFS S3 is not reachable."""
    if not _is_seaweedfs_reachable():
        pytest.skip(
            f"SeaweedFS S3 endpoint not reachable at {SEAWEEDFS_S3_ENDPOINT}. "
            "Start the stack with `docker compose up` before running integration tests."
        )


@pytest.fixture(scope="session")
def require_mongodb():
    """Skip if MongoDB is not reachable at localhost:27017."""
    if not _is_mongodb_reachable():
        pytest.skip(
            "MongoDB not reachable at localhost:27017. "
            "Start with `docker compose up mongodb`."
        )


@pytest.fixture
async def test_db(require_mongodb):
    """Yield a Motor test database, then drop test collections after each test."""
    from motor.motor_asyncio import AsyncIOMotorClient

    client = AsyncIOMotorClient(MONGODB_TEST_URL)
    db = client[MONGODB_TEST_DB]
    yield db
    # cleanup: drop test collections after each test
    await db.users.drop()
    await db.audit_events.drop()
    client.close()
