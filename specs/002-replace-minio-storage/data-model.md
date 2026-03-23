# Data Model: Replace MinIO with Open-Source S3-Compatible Storage

**Feature**: `002-replace-minio-storage`  
**Phase**: 1 — Design  
**Date**: 2026-03-23

## Overview

This feature introduces no new application data models. The change is purely an infrastructure swap at the object-storage layer. The existing bucket/key naming conventions and object type conventions are unchanged.

This document captures the **storage layout model** — how application data is organised within the S3-compatible store — to serve as a reference for the implementation and for future storage-related features.

---

## Storage Layout Model

### Provider

**SeaweedFS** (replaces MinIO) — single-node, S3-compatible.

### Bucket

| Name | Purpose | Created by |
|------|---------|-----------|
| `rift-artifacts` | All application binary blobs | `storage-init` container on first boot |

There is one bucket for all artifact types. Objects are organised by key prefix conventions (see below).

### Object Key Structure

All keys follow a deterministic path pattern derived from application identifiers:

```
{object-type}/{run_id}/{workspace_id}.{extension}
```

| Prefix | Extension | Content-Type | Written by | Read by |
|--------|-----------|-------------|-----------|--------|
| `logs/` | `.log` | `text/plain` | Worker (`put_log`) | API (log streaming), audit |
| `patches/` | `.patch` | `text/plain` | Worker (`put_patch`) | API, changeset viewer |

**Examples:**
```
logs/run-abc123/workspace-xyz789.log
patches/run-abc123/workspace-xyz789.patch
```

### Key Generation (from `S3ObjectStoreAdapter`)

```python
# put_log
key = f"logs/{run_id}/{workspace_id}.log"

# put_patch
key = f"patches/{run_id}/{workspace_id}.patch"
```

These key patterns are unchanged by this migration.

---

## Configuration Model

The storage service is configured via two mechanisms:

### 1. Docker Compose Environment Variables (application-side)

| Variable | Value (local dev) | Description |
|----------|------------------|-------------|
| `OBJECT_STORE_ENDPOINT` | `http://seaweedfs:9000` | S3 API endpoint (Docker-internal) |
| `OBJECT_STORE_BUCKET` | `rift-artifacts` | Target bucket name |
| `OBJECT_STORE_ACCESS_KEY` | `minioadmin` | S3 access key (matches identity in s3-config.json) |
| `OBJECT_STORE_SECRET_KEY` | `minioadmin` | S3 secret key (matches identity in s3-config.json) |
| `OBJECT_STORE_REGION` | `us-east-1` | Region (SeaweedFS accepts any value; kept for boto3 compatibility) |

### 2. SeaweedFS Identity Config (`infra/seaweedfs/s3-config.json`)

```json
{
  "identities": [
    {
      "name": "riftdev",
      "credentials": [
        {
          "accessKey": "minioadmin",
          "secretKey": "minioadmin"
        }
      ],
      "actions": [
        "Read",
        "Write",
        "List",
        "Tagging",
        "Admin"
      ]
    }
  ]
}
```

**The access key / secret key values in `s3-config.json` MUST match `OBJECT_STORE_ACCESS_KEY` and `OBJECT_STORE_SECRET_KEY` in `docker-compose.yml`.** If they diverge, presigned URL signature validation will fail.

---

## State Transitions

Object lifecycle within the store:

```
[Worker executes workspace]
        │
        ▼
  put_log(run_id, workspace_id, log_content)
  put_patch(run_id, workspace_id, patch_content)
        │
        ▼
  [Object exists in bucket]
        │
        ├──▶ get_object(key)          → API serves log/diff viewers
        ├──▶ generate_presigned_url() → API returns time-limited download link
        └──▶ delete_object(key)       → Cleanup / TTL management (future)
```

---

## Constraints and Invariants

1. **Bucket must exist before the first `PutObject`** — enforced by the `storage-init` init container using `condition: service_completed_successfully`.
2. **Key uniqueness** — keys are derived from `run_id` + `workspace_id`, both of which are application-level UUIDs. Collisions are theoretically possible only on UUID collision (negligible probability).
3. **Object immutability** — once written, objects are not updated; if a re-run occurs it uses a new `run_id`.
4. **No lifecycle policy** — object deletion is not currently automated. Storage grows unbounded unless manually pruned. This is acceptable for local dev.
5. **No encryption at rest** — SeaweedFS does not encrypt stored data by default. Acceptable for local dev only. Production deployments must use encrypted volumes.

---

## No New Domain Model Entities

This feature does not introduce any new MongoDB collections, Redis keys, API request/response schemas, or domain model classes. The `S3ObjectStoreAdapter` class remains unchanged.
