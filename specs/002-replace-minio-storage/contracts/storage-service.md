# Contract: Object Storage Service (SeaweedFS)

**Feature**: `002-replace-minio-storage`  
**Type**: Infrastructure service contract  
**Date**: 2026-03-23

---

## Service Contract

This document defines the interface contract between the Rift application (API service, worker) and the object-storage infrastructure service. The contract is fulfilled by any S3-compatible storage backend. The implementation for local development is **SeaweedFS**.

---

## Docker Compose Service Definition

### Service: `seaweedfs`

| Property | Value |
|----------|-------|
| Image | `chrislusf/seaweedfs:3.71` |
| Container name | `rift-seaweedfs` |
| Restart policy | `unless-stopped` |

**Exposed ports (host → container):**

| Host port | Container port | Protocol | Purpose |
|-----------|---------------|----------|---------|
| `9000` | `9000` | HTTP | S3-compatible API |
| `8888` | `8888` | HTTP | Filer web UI (browser access) |

**Volume:**

| Name | Mount path | Purpose |
|------|------------|---------|
| `seaweedfs_data` | `/data` | Persistent object + metadata storage |

**Bind mount:**

| Host path | Container path | Mode | Purpose |
|-----------|---------------|------|---------|
| `./infra/seaweedfs/s3-config.json` | `/etc/seaweedfs/s3-config.json` | `ro` | S3 identity/auth config |

**Command flags:**

```
server
  -s3                              # Enable S3 gateway
  -s3.port=9000                    # S3 API listens on 9000
  -s3.config=/etc/seaweedfs/s3-config.json  # Auth identities
  -filer                           # Enable filer (required for S3)
  -volume.max=100                  # Max volume count
  -master.volumeSizeLimitMB=200    # Max volume size (200 MB, dev-appropriate)
  -ip.bind=0.0.0.0                 # Bind to all interfaces
```

**Health check:**

```yaml
test: ["CMD-SHELL", "wget -q --spider http://localhost:9333/cluster/status || exit 1"]
interval: 10s
timeout: 5s
retries: 5
start_period: 15s
```

The health check queries the master cluster status endpoint; a 200 response indicates the S3 gateway is ready to accept requests.

---

### Service: `storage-init` (init container)

| Property | Value |
|----------|-------|
| Image | `amazon/aws-cli:2.15.37` |
| Container name | `rift-storage-init` |
| Restart policy | `"no"` |
| Depends on | `seaweedfs` (condition: `service_healthy`) |

**Purpose**: Creates the `rift-artifacts` bucket on first boot. Exits 0 on success (including when the bucket already exists).

**Environment variables (internal to init container):**

| Variable | Value | Notes |
|----------|-------|-------|
| `AWS_ACCESS_KEY_ID` | `minioadmin` | Must match identity in `s3-config.json` |
| `AWS_SECRET_ACCESS_KEY` | `minioadmin` | Must match identity in `s3-config.json` |
| `AWS_DEFAULT_REGION` | `us-east-1` | Required by AWS CLI; SeaweedFS ignores the value |

**Command:**

```sh
/bin/sh -c "
  aws s3api create-bucket \
    --bucket rift-artifacts \
    --endpoint-url http://seaweedfs:9000 \
    2>/dev/null || true &&
  echo 'Bucket rift-artifacts ready.'
"
```

**Idempotency**: The `|| true` ensures the container exits 0 even if the bucket already exists (`BucketAlreadyOwnedByYou` / `BucketAlreadyExists`).

---

## S3 API Operations Contract

The application relies on the following S3 API operations. All MUST be supported by any storage backend used in this role.

| Operation | HTTP method | Used in | Expected behaviour |
|-----------|-------------|--------|-------------------|
| `PutObject` | `PUT /bucket/key` | `put_object`, `put_log`, `put_patch` | Returns HTTP 200 on success |
| `GetObject` | `GET /bucket/key` | `get_object` | Returns object bytes; raises `NoSuchKey` (404) for missing keys |
| `DeleteObject` | `DELETE /bucket/key` | `delete_object` | Returns HTTP 204 on success |
| `GetObject` (presigned) | `GET /bucket/key?X-Amz-*` | `generate_presigned_url` | URL valid for `expires_in` seconds; signed with Signature V4 |

**Error contract for missing keys:**

```python
# S3ObjectStoreAdapter.get_object raises:
FileNotFoundError(f"Object not found: {key}")
# when ClientError with Code == "NoSuchKey" is raised by boto3.
```

Any storage replacement MUST return a `NoSuchKey` error code for non-existent objects to preserve this error contract.

---

## Application Environment Variables

These variables configure the application's connection to the storage service. Names are fixed (FR-008).

| Variable | Example value (local dev) | Description |
|----------|--------------------------|-------------|
| `OBJECT_STORE_ENDPOINT` | `http://seaweedfs:9000` | S3 API base URL (Docker-internal) |
| `OBJECT_STORE_BUCKET` | `rift-artifacts` | Bucket name for all application artifacts |
| `OBJECT_STORE_ACCESS_KEY` | `minioadmin` | S3 access key |
| `OBJECT_STORE_SECRET_KEY` | `minioadmin` | S3 secret key |
| `OBJECT_STORE_REGION` | `us-east-1` | AWS region (used by boto3; any valid region string accepted) |

---

## Dependency Graph

```
mongodb (service_healthy)  ──┐
redis   (service_healthy)  ──┤──▶ api
temporal (service_started) ──┤──▶ worker
storage-init (service_completed_successfully) ──┘
       │
       └──▶ depends on ──▶ seaweedfs (service_healthy)
```

**Critical constraint**: `storage-init` must exit with code 0 before API or worker start. Use `condition: service_completed_successfully` in Docker Compose.

---

## Access URLs (Local Development)

| Service | URL | Notes |
|---------|-----|-------|
| S3 API | `http://localhost:9000` | Used by boto3 clients from host (e.g., tests) |
| Filer web UI | `http://localhost:8888` | Browse buckets and objects in browser |
| S3 API (internal) | `http://seaweedfs:9000` | Used by API/worker containers inside Docker network |
