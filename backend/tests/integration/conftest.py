"""Integration test fixtures — skips suite if required services are unreachable."""

from __future__ import annotations

import pytest
import requests


SEAWEEDFS_S3_ENDPOINT = "http://localhost:9000"


def _is_seaweedfs_reachable() -> bool:
    try:
        requests.head(SEAWEEDFS_S3_ENDPOINT, timeout=3)
        return True
    except requests.exceptions.ConnectionError:
        return False


@pytest.fixture(scope="session", autouse=True)
def require_seaweedfs() -> None:
    """Skip the entire integration suite if SeaweedFS S3 is not reachable."""
    if not _is_seaweedfs_reachable():
        pytest.skip(
            f"SeaweedFS S3 endpoint not reachable at {SEAWEEDFS_S3_ENDPOINT}. "
            "Start the stack with `docker compose up` before running integration tests."
        )
