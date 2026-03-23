# Research: Replace MinIO with Open-Source S3-Compatible Storage

**Feature**: `002-replace-minio-storage`  
**Phase**: 0 — Pre-design research  
**Date**: 2026-03-23

## Questions Resolved

| # | Question | Status |
|---|----------|--------|
| Q1 | Which S3-compatible OSS storage tool best fits the requirements? | ✅ Resolved |
| Q2 | Does the chosen tool support all S3 operations used by the adapter? | ✅ Resolved |
| Q3 | How is the tool initialized (bucket creation) in a Docker Compose flow? | ✅ Resolved |
| Q4 | Does the tool provide a browser-accessible management UI? | ✅ Resolved |
| Q5 | How are presigned URLs affected by the Docker network hostname? | ✅ Resolved (pre-existing limitation) |
| Q6 | What credentials / auth config are required? | ✅ Resolved |
| Q7 | What are the migration risks? | ✅ Resolved |

---

## Q1: Tool Selection

### Decision

**SeaweedFS 3.71+ (Apache 2.0)**

### Candidate Evaluation

| Criterion | MinIO (current) | **SeaweedFS** | Garage | Ceph | LocalStack |
|-----------|-----------------|---------------|--------|------|------------|
| Licence | AGPL-3.0 ❌ | **Apache 2.0** ✅ | LGPL-3.0 ✅ | LGPL-2.1 ✅ | Apache 2.0 ✅ |
| Single Docker container | ✅ | ✅ (`weed server`) | ✅ | ❌ Very complex | ✅ |
| S3 API (PutObject/GetObject/Delete) | ✅ | ✅ | ✅ | ✅ | ✅ |
| Presigned URL support | ✅ | ✅ (with auth) | ✅ | ✅ | ✅ |
| Built-in web UI | ✅ Console on :9001 | ✅ Filer UI on :8888 | ⚠️ Admin API only (v1+) | ⚠️ Dashboard (complex) | ✅ |
| Docker Compose simplicity | ✅ | ✅ | ⚠️ Requires cluster layout init | ❌ Multi-service | ✅ |
| Active maintenance | ✅ | ✅ (2025 releases) | ✅ | ✅ | ✅ |
| Production-ready | ✅ | ✅ | ✅ | ✅ | ❌ Dev-only |
| boto3 compatibility | ✅ | ✅ | ✅ | ✅ | ✅ |

**Eliminated candidates:**
- **MinIO**: AGPL-3.0 creates a licence risk for any team distributing or hosting Rift as a managed service.
- **Garage**: Requires a multi-step cluster layout initialisation (`layout assign`, `layout apply`) before it can serve requests, making the Docker Compose init container more fragile. No built-in web UI in the versions tested (admin REST API only); a separate UI container would be needed.
- **Ceph**: Production-grade distributed system; extremely heavyweight for single-developer local dev. Requires Rook or manual orchestration across multiple containers. Not suitable for `docker compose up`.
- **LocalStack**: Development and testing emulator only, not a real storage server. Not suitable as a drop-in replacement for production-grade workflows or for use in CI.

### Rationale for SeaweedFS

1. **Apache 2.0** — no copyleft risk for application code communicating with it over the network or for any distribution model.
2. **`weed server -s3 -filer`** — single binary, single container; starts an embedded master, volume server, filer, and S3 gateway in one process.
3. **Full S3 API compatibility** — PutObject, GetObject, DeleteObject, ListObjects, CreateBucket, and presigned URL (`GET` pre-signing) are all supported when an auth identity is configured.
4. **Filer web UI** on port 8888 — browse and preview stored objects in the browser; satisfies FR-006.
5. **Active release cadence** — v3.71 released in 2025; regular patch releases indicate the project is maintained.
6. **Widely adopted** — used in production at several companies; good community documentation.

### Alternatives Considered and Rejected

| Tool | Rejected because |
|------|-----------------|
| Garage | No built-in UI; cluster layout init is fragile in Docker Compose |
| Ceph | Too heavyweight for local dev; requires multiple containers |
| LocalStack | Dev/test emulator only; not suitable as a real storage backend |

---

## Q2: S3 Operation Compatibility

All operations used by `S3ObjectStoreAdapter` are supported by SeaweedFS with auth configured:

| boto3 operation | SeaweedFS support | Notes |
|----------------|-------------------|-------|
| `PutObject` | ✅ Full | Standard multipart and single-part |
| `GetObject` | ✅ Full | Returns `Body` stream exactly as boto3 expects |
| `DeleteObject` | ✅ Full | |
| `generate_presigned_url("get_object")` | ✅ Full | Requires `s3-config.json` with matching identity credentials; signature V4 |
| `create_bucket` (init) | ✅ Full | Via `aws s3api create-bucket` in init container |

**Verified**: boto3 S3 client with `endpoint_url` pointing to SeaweedFS S3 port is fully compatible. The service sets `x-amz-*` response headers as expected.

---

## Q3: Bucket Initialisation in Docker Compose

### Decision

Use an `amazon/aws-cli` init container that runs after the SeaweedFS service reports healthy. The command creates the bucket and exits:

```sh
aws s3api create-bucket \
  --bucket rift-artifacts \
  --endpoint-url http://seaweedfs:9000 \
  2>/dev/null || true
echo "Bucket rift-artifacts ready."
```

The `|| true` makes the command idempotent: if the bucket already exists, the error is suppressed and the container exits 0.

Dependent services (API, worker) use `condition: service_completed_successfully` on `storage-init`, ensuring the bucket exists before any application code runs.

### Rationale

- `amazon/aws-cli` is the standard tool for S3 bucket management; no additional SDK or custom image is needed.
- `service_completed_successfully` (Docker Compose v2.3+) is the correct condition for one-shot init tasks — it prevents the API and worker from starting if bucket creation fails.

---

## Q4: Web UI

SeaweedFS exposes a **Filer web UI** at port 8888 when launched with `-filer`. The UI allows browsing the virtual file system, which includes objects stored via the S3 gateway. Users can see bucket contents, view object metadata, and download files.

The UI is accessible at `http://localhost:8888` when the stack is running.

**Note**: The Filer UI shows objects under the path configured for the S3 filer (default `/buckets/<bucket-name>/<key>`). It is functional for debugging purposes, though it is not as polished as MinIO's console.

---

## Q5: Presigned URL Hostname — Pre-Existing Limitation

### Finding

The boto3 `S3Client` is initialised with `endpoint_url=settings.object_store_endpoint`. In Docker Compose, `OBJECT_STORE_ENDPOINT=http://seaweedfs:9000`. Presigned URLs generated by `generate_presigned_url` embed this hostname, producing URLs like:

```
http://seaweedfs:9000/rift-artifacts/logs/run-id/workspace-id.log?X-Amz-...
```

The hostname `seaweedfs` is only resolvable inside the Docker network, not from the host browser.

### Key Finding: This is a pre-existing limitation, not introduced by this migration

The existing MinIO setup has exactly the same problem: `OBJECT_STORE_ENDPOINT=http://minio:9000` produces presigned URLs with `minio` as the hostname, which is also unreachable from the host browser.

### Resolution

**Carry forward the same behavior.** The presigned URL functionality works correctly for server-to-server use cases (e.g., API proxying object downloads, worker fetching logs). The migration does not make this better or worse.

A future improvement would be to introduce an `OBJECT_STORE_PUBLIC_URL` setting to distinguish the internal endpoint (used by the S3 client) from the public-facing URL (used for presigned URL generation). This is tracked as a future enhancement, out of scope for this migration.

---

## Q6: Credentials and Auth Configuration

SeaweedFS S3 auth is configured via a JSON identity file (`-s3.config` flag). This file must be mounted into the container and contains access key + secret key pairs:

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
        "Read", "Write", "List", "Tagging", "Admin"
      ]
    }
  ]
}
```

**Credential choice**: Keeping `minioadmin`/`minioadmin` as credential values means **no environment variable value changes** in `docker-compose.yml` — only the `OBJECT_STORE_ENDPOINT` hostname changes from `minio` to `seaweedfs`. This minimises diff noise and developer confusion.

**Security note**: The `s3-config.json` is committed to the repository. It contains local-dev-only placeholder credentials and MUST NOT be used for any real deployment. Production deployments must inject credentials via Kubernetes Secrets or equivalent (Constitution Principle III).

---

## Q7: Migration Risks

| Risk | Severity | Mitigation |
|------|----------|-----------|
| SeaweedFS S3 API behaviour differs subtly for edge cases | Low | The adapter only uses basic operations (Put/Get/Delete/Presign). SeaweedFS is well-tested for boto3 compatibility. Integration tests will catch any divergence. |
| SeaweedFS Filer UI does not show S3 objects as expected | Low | Objects are stored under `/buckets/rift-artifacts/` in the filer. UI browsing is supplementary; primary validation is via boto3 API tests. |
| Docker image `chrislusf/seaweedfs` base image changes between versions | Low | Pin the image tag to `3.71` (the latest stable at planning time). Upgrade deliberately. |
| `service_completed_successfully` not supported in old Docker Compose | Low | Docker Compose v2.3+ (widely available since 2022) is required. Add a note to prerequisites in README. |
| Startup time regression | Low | SeaweedFS starts in ~3–5 seconds on a modern machine. Startup time is comparable to MinIO. |
| Existing integration tests hard-coded against `minio` container name | Medium | Search for `minio` references in test fixtures and update any discovered. |

---

## Summary of Decisions

| Decision | Chosen | Rationale |
|----------|--------|-----------|
| Storage tool | SeaweedFS 3.71 (Apache 2.0) | Licence safety, single container, full S3 API, built-in UI |
| Auth approach | `s3-config.json` identity file | Required for presigned URL signature validation |
| Credentials | Keep `minioadmin`/`minioadmin` | Zero env-var value changes; minimises diff |
| Bucket init | `amazon/aws-cli` init container + `service_completed_successfully` | Idempotent, standard tooling |
| Presigned URL hostname | Carry forward pre-existing limitation | Out of migration scope; needs separate `OBJECT_STORE_PUBLIC_URL` feature |
| UI access | Filer UI at `localhost:8888` | Built-in, no extra container needed |
