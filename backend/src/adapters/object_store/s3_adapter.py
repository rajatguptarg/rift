from __future__ import annotations

import boto3
from botocore.exceptions import ClientError

from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)


class S3ObjectStoreAdapter:
    """S3-compatible adapter for storing execution logs and patch files."""

    def __init__(self) -> None:
        self._client = boto3.client(
            "s3",
            endpoint_url=settings.object_store_endpoint,
            aws_access_key_id=settings.object_store_access_key,
            aws_secret_access_key=settings.object_store_secret_key,
            region_name=settings.object_store_region,
        )
        self._bucket = settings.object_store_bucket

    def put_object(self, key: str, body: bytes, content_type: str = "application/octet-stream") -> None:
        self._client.put_object(
            Bucket=self._bucket,
            Key=key,
            Body=body,
            ContentType=content_type,
        )
        logger.debug("Object stored", key=key, bucket=self._bucket)

    def get_object(self, key: str) -> bytes:
        try:
            response = self._client.get_object(Bucket=self._bucket, Key=key)
            return response["Body"].read()
        except ClientError as exc:
            if exc.response["Error"]["Code"] == "NoSuchKey":
                raise FileNotFoundError(f"Object not found: {key}") from exc
            raise

    def delete_object(self, key: str) -> None:
        self._client.delete_object(Bucket=self._bucket, Key=key)

    def generate_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        return self._client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self._bucket, "Key": key},
            ExpiresIn=expires_in,
        )

    # ── Convenience helpers ───────────────────────────────────────────────────

    def put_log(self, run_id: str, workspace_id: str, log_content: str) -> str:
        key = f"logs/{run_id}/{workspace_id}.log"
        self.put_object(key, log_content.encode(), "text/plain")
        return key

    def put_patch(self, run_id: str, workspace_id: str, patch: str) -> str:
        key = f"patches/{run_id}/{workspace_id}.patch"
        self.put_object(key, patch.encode(), "text/plain")
        return key
