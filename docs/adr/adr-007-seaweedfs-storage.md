# ADR-007: Replace MinIO with SeaweedFS for Local Development Object Storage

**Status**: Accepted  
**Date**: 2026-03-23  
**Deciders**: Rift Platform Team  
**Feature Branch**: `002-replace-minio-storage`

---

## Context

Rift uses an S3-compatible object store for persisting execution artifacts — execution logs and patch files — produced by the Temporal worker during batch change runs. The initial implementation used **MinIO** as the S3-compatible backend in the local development Docker Compose stack.

**MinIO changed its licence from Apache 2.0 to AGPL-3.0 in October 2021 (server) and January 2022 (client tools).** Under AGPL-3.0, any organisation that runs MinIO as part of a service offered over a network must open-source their entire application stack under AGPL-3.0 or obtain a commercial licence. While this restriction applies to _network service_ use, not merely internal use, the uncertainty and legal overhead are unacceptable for a project like Rift that is intended to be self-hosted or offered as a managed service by adopters.

Additionally, MinIO's shift to a commercial-first model means the open-source version (AGPL) no longer receives the same level of feature investment, and the project has moved significant functionality into the commercial Operator tier.

The replacement must:
1. Be licensed under Apache 2.0, LGPL, or a similarly permissive open-source licence.
2. Expose a full S3-compatible API (PutObject, GetObject, DeleteObject, presigned URLs).
3. Run as a single Docker container or minimal container set suitable for `docker compose up`.
4. Provide a browser-accessible management UI.
5. Not require changes to the application's `S3ObjectStoreAdapter` or environment variable schema.

---

## Decision

**Replace MinIO with SeaweedFS (Apache 2.0, chrislusf/seaweedfs).**

SeaweedFS is run via its `weed server` unified mode with the S3 gateway (`-s3`) and Filer (`-filer`) components enabled. A single container starts all required sub-services (master, volume, filer, S3 gateway) via one Docker image.

The `s3-config.json` identity file is committed to the repository with local-dev placeholder credentials (`minioadmin`/`minioadmin`) and mounted read-only into the SeaweedFS container.

A new `storage-init` init container (using `amazon/aws-cli`) checks whether the `rift-artifacts` bucket already exists and creates it only when missing. This keeps repeated `docker compose up --build` and `make docker-up-build` runs idempotent. Application services depend on `storage-init` completing successfully via Docker Compose's `service_completed_successfully` condition.

---

## Alternatives Considered

### Garage (LGPL-3.0)

**Rejected.** Garage requires a cluster layout initialisation step (`layout assign`, `layout apply`) before it becomes operational. This step is fragile in a Docker Compose init-container pattern because it requires querying the node ID at runtime. Additionally, Garage does not have a built-in browser UI as of the versions evaluated (v1.x provides an admin REST API only; a separate UI container would be required). The operational overhead exceeds what is justified for a local-dev replacement.

### Ceph (LGPL-2.1)

**Rejected.** Ceph is a production-grade distributed storage system. Running a functional Ceph cluster for local development requires multiple containers (monitor, manager, OSD, RGW) and significant configuration. It is not suitable for a single-command `docker compose up` workflow for developers.

### LocalStack (Apache 2.0)

**Rejected.** LocalStack is a development and testing emulator, not a production-grade storage server. It does not maintain durable storage across container restarts in the same way a real storage server does, and it is explicitly designed as a test double rather than a real service. Using it as the storage backend would mean the development environment diverges from production behaviour.

### Zenko CloudServer / Scality S3 Server (Apache 2.0)

**Rejected.** While CloudServer is S3-compatible and open-source, it is primarily maintained as part of Scality's commercial product ecosystem. Development activity on the standalone community version has slowed significantly. SeaweedFS offers better long-term maintenance prospects.

---

## Consequences

### Positive

- **Licence safety**: SeaweedFS is Apache 2.0. There is no copyleft risk for any deployment model.
- **Zero application code change**: `S3ObjectStoreAdapter`, environment variable names, bucket name, and key conventions are all unchanged.
- **Single container**: `weed server -s3 -filer` provides a complete storage solution in one Docker image — no multi-container orchestration.
- **Built-in web UI**: The Filer UI at port 8888 provides object browsing for debugging, replacing the MinIO console.
- **Active maintenance**: SeaweedFS receives regular releases with active community support.

### Negative / Trade-offs

- **New configuration file**: `infra/seaweedfs/s3-config.json` must be maintained. If credentials are rotated in `docker-compose.yml`, the config file must be updated in sync.
- **Filer UI is less polished than MinIO console**: The SeaweedFS Filer UI is functional but does not offer the same level of UI refinement as MinIO's console. This is acceptable for local dev debugging.
- **Startup time**: SeaweedFS's unified server mode starts multiple embedded sub-services, which may add 5–10 seconds of startup time compared to MinIO. The health check's `start_period: 15s` accommodates this.
- **Presigned URL host limitation carries forward**: Presigned URLs generated by the application embed the internal Docker hostname (`seaweedfs`), which is unreachable from a host browser. This is a pre-existing limitation from the MinIO setup and is out of scope for this migration. A future `OBJECT_STORE_PUBLIC_URL` configuration field is recommended to address it.

### Neutral

- The `OBJECT_STORE_ENDPOINT` value changes from `http://minio:9000` to `http://seaweedfs:9000`. All other environment variable names and values remain identical.
- The storage volume is renamed from `minio_data` to `seaweedfs_data`. Existing local `minio_data` volumes can be removed after migration.

---

## References

- [SeaweedFS GitHub](https://github.com/seaweedfs/seaweedfs)
- [SeaweedFS S3 API docs](https://github.com/seaweedfs/seaweedfs/wiki/Amazon-S3-API)
- [MinIO AGPL licence change announcement (2021)](https://blog.min.io/from-open-source-to-free-and-open-source-minio-is-now-fully-licensed-under-gnu-agplv3/)
- [Feature spec](../../specs/002-replace-minio-storage/spec.md)
- [Research findings](../../specs/002-replace-minio-storage/research.md)
- Supersedes: none
- See also: [ADR-001 MongoDB Primary Store](adr-001-mongodb-primary-store.md)
