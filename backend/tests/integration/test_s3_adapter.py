"""Integration tests for S3ObjectStoreAdapter against SeaweedFS.

Requires a running SeaweedFS instance at http://localhost:9000.
The conftest.py fixture automatically skips this suite if the endpoint
is not reachable.
"""

from __future__ import annotations

import uuid

import pytest

from src.adapters.object_store.s3_adapter import S3ObjectStoreAdapter


@pytest.fixture()
def adapter() -> S3ObjectStoreAdapter:
    """Return an S3ObjectStoreAdapter using default local-dev settings."""
    return S3ObjectStoreAdapter()


@pytest.fixture()
def unique_key() -> str:
    """Return a unique S3 key for each test to avoid collisions."""
    return f"test-integration/{uuid.uuid4().hex}"


class TestS3ObjectStoreAdapterIntegration:
    def test_put_and_get_object(self, adapter: S3ObjectStoreAdapter, unique_key: str) -> None:
        body = b"hello seaweedfs integration test"
        adapter.put_object(unique_key, body, content_type="text/plain")
        result = adapter.get_object(unique_key)
        assert result == body

    def test_delete_object_and_get_raises(
        self, adapter: S3ObjectStoreAdapter, unique_key: str
    ) -> None:
        body = b"temporary object"
        adapter.put_object(unique_key, body)
        adapter.delete_object(unique_key)
        with pytest.raises(FileNotFoundError):
            adapter.get_object(unique_key)

    def test_put_log_returns_expected_key_pattern(
        self, adapter: S3ObjectStoreAdapter
    ) -> None:
        run_id = uuid.uuid4().hex
        workspace_id = uuid.uuid4().hex
        key = adapter.put_log(run_id, workspace_id, "log line 1\nlog line 2\n")
        assert key == f"logs/{run_id}/{workspace_id}.log"

    def test_put_patch_returns_expected_key_pattern(
        self, adapter: S3ObjectStoreAdapter
    ) -> None:
        run_id = uuid.uuid4().hex
        workspace_id = uuid.uuid4().hex
        patch_content = "--- a/file.py\n+++ b/file.py\n@@ -1 +1 @@\n-old\n+new\n"
        key = adapter.put_patch(run_id, workspace_id, patch_content)
        assert key == f"patches/{run_id}/{workspace_id}.patch"
