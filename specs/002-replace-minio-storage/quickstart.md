# Quickstart: After MinIO → SeaweedFS Migration

**Feature**: `002-replace-minio-storage`  
**Audience**: Developers setting up the local stack after this change is merged  
**Date**: 2026-03-23

---

## What Changed

The local-dev object storage service has changed from **MinIO** (AGPL-3.0) to **SeaweedFS** (Apache 2.0). SeaweedFS is an S3-compatible open-source storage server. The change is transparent to application code — all environment variable names, the bucket name, and the S3 API contract are unchanged.

| Before | After |
|--------|-------|
| `minio/minio:RELEASE.2024-01-16` | `chrislusf/seaweedfs:3.71` |
| S3 API on port `9000` | S3 API on port `9000` (same) |
| Console on port `9001` | Filer UI on port `8888` |
| `OBJECT_STORE_ENDPOINT=http://minio:9000` | `OBJECT_STORE_ENDPOINT=http://seaweedfs:9000` |

---

## Prerequisites

- Docker Desktop ≥ 4.25 (includes Docker Compose v2.24+)
- `docker compose version` must report **v2.3 or later** (required for `service_completed_successfully` condition)

---

## First-Time Setup (Clean State)

```bash
# 1. Pull the latest changes
git pull origin main

# 2. Remove old MinIO volumes (only if you had them from before)
docker volume rm rift_minio_data 2>/dev/null || true

# 3. Start the full stack (builds images, creates SeaweedFS volume, creates bucket)
docker compose up --build
```

The `storage-init` container will run automatically to create the `rift-artifacts` bucket. You will see:

```
rift-storage-init  | Bucket rift-artifacts ready.
rift-storage-init exited with code 0
```

The API and worker start only after this completes successfully.

---

## Subsequent Runs

```bash
docker compose up
```

The bucket already exists — `storage-init` will handle this gracefully and exit 0.

---

## Access Points

| Service | URL | Credentials |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | — |
| API / Swagger docs | http://localhost:8000/docs | — |
| Temporal UI | http://localhost:8088 | — |
| **SeaweedFS Filer UI** | **http://localhost:8888** | No auth required |
| SeaweedFS S3 API (host) | http://localhost:9000 | `minioadmin` / `minioadmin` |

---

## Browsing Stored Artifacts

1. Open **http://localhost:8888** in your browser.
2. Navigate to **`/buckets/rift-artifacts/`** to see stored logs and patches.
3. Objects are organised as:
   - `/buckets/rift-artifacts/logs/<run-id>/<workspace-id>.log`
   - `/buckets/rift-artifacts/patches/<run-id>/<workspace-id>.patch`

---

## Testing Storage Directly (from Host)

You can interact with the SeaweedFS S3 API from the host using AWS CLI or boto3:

```bash
# List objects in the bucket
aws s3 ls s3://rift-artifacts/ \
  --endpoint-url http://localhost:9000 \
  --no-sign-request

# Or with credentials
AWS_ACCESS_KEY_ID=minioadmin \
AWS_SECRET_ACCESS_KEY=minioadmin \
aws s3 ls s3://rift-artifacts/ \
  --endpoint-url http://localhost:9000
```

---

## Troubleshooting

### `storage-init` exits with non-zero code

Check the init container logs:

```bash
docker logs rift-storage-init
```

Common cause: SeaweedFS was not fully started when the init container ran. Try:

```bash
docker compose restart storage-init
```

If the issue persists, restart the full stack:

```bash
docker compose down && docker compose up
```

### SeaweedFS health check failing

```bash
docker logs rift-seaweedfs
```

SeaweedFS requires ~10–15 seconds to start up its master + volume + filer components. The health check has a `start_period: 15s` grace period. If the service never becomes healthy, check for port conflicts on `9000` or `8888`.

### Port conflict on 9000 or 8888

Another service may be using these ports. Check:

```bash
lsof -i :9000
lsof -i :8888
```

Stop the conflicting service or change the host port mappings in `docker-compose.yml`.

### API or worker cannot connect to storage

Verify the `OBJECT_STORE_ENDPOINT` environment variable is correct inside the container:

```bash
docker exec rift-api env | grep OBJECT_STORE
# Expected: OBJECT_STORE_ENDPOINT=http://seaweedfs:9000
```

---

## Resetting Storage State

To wipe all stored artifacts and start fresh:

```bash
docker compose down -v              # removes all named volumes including seaweedfs_data
docker compose up --build           # recreates storage + bucket from scratch
```

---

## Running Backend Tests Against SeaweedFS

Integration tests that interact with the object store should spin up the SeaweedFS container (or use the running stack). The test configuration should point to `http://localhost:9000`:

```python
# In test configuration / conftest.py
OBJECT_STORE_ENDPOINT = "http://localhost:9000"
OBJECT_STORE_ACCESS_KEY = "minioadmin"
OBJECT_STORE_SECRET_KEY = "minioadmin"
OBJECT_STORE_BUCKET = "rift-artifacts"
```

Run the integration test suite with the stack running:

```bash
docker compose up -d mongodb redis temporal seaweedfs storage-init
pytest tests/integration/ -v
```
