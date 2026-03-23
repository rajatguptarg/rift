# Feature Specification: Replace MinIO with Open-Source S3-Compatible Storage

**Feature Branch**: `002-replace-minio-storage`  
**Created**: 2026-03-23  
**Status**: Accepted  
**Input**: User description: "the app uses minio as s3 storage which is deprecated now. Use ceph or some other opensource tool as storage which can be run with docker and update the docker-compose to run the entire app."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Developer Starts Full Local Stack Without Storage Errors (Priority: P1)

A developer clones the repository and runs a single command to start the entire application stack locally. The object storage service starts successfully, the required bucket is automatically created, and the API and worker can store and retrieve artifacts (execution logs, patch files) without errors.

**Why this priority**: This is the core motivation for the change — MinIO is deprecated and the local development environment must be reliably runnable. Without working storage, batch change execution fails completely.

**Independent Test**: Can be fully tested by running `docker compose up` from a clean checkout and verifying the API health endpoint returns healthy, the storage bucket exists, and a test artifact can be written and read back.

**Acceptance Scenarios**:

1. **Given** the repository has been cloned with no prior Docker volumes, **When** the developer runs `docker compose up`, **Then** all services including the storage service reach a healthy state within 3 minutes
2. **Given** the stack is running, **When** the API receives a request that triggers artifact storage (log or patch write), **Then** the artifact is persisted in the storage bucket without error
3. **Given** the stack is running, **When** the API retrieves a previously stored artifact, **Then** the correct content is returned

---

### User Story 2 - Developer Inspects Stored Artifacts via a Web UI (Priority: P2)

A developer needs to inspect stored execution logs or patch files to debug a batch change run. They open a browser-based management interface for the object storage service to browse buckets and download objects.

**Why this priority**: Observability into stored artifacts is important for debugging. MinIO provided a console UI; the replacement must offer equivalent visibility into stored data.

**Independent Test**: Can be fully tested by storing a known artifact, then navigating to the storage management UI in a browser and confirming the object is visible and downloadable.

**Acceptance Scenarios**:

1. **Given** the stack is running, **When** the developer navigates to the storage management UI URL in a browser, **Then** they can see the `rift-artifacts` bucket and browse its contents
2. **Given** an artifact has been written by the worker, **When** the developer views the bucket in the UI, **Then** the artifact key is listed and its content can be downloaded

---

### User Story 3 - Existing Application Behaviour Is Unchanged After Migration (Priority: P3)

All existing application features that depend on object storage — execution log upload, patch file storage, presigned URL generation — continue to work after the migration with no changes to application business logic or configuration contract.

**Why this priority**: The migration must be transparent to the rest of the application. The S3-compatible interface contract must be preserved so no backend code changes are required.

**Independent Test**: Can be fully tested by running the existing test suite and executing an end-to-end batch change run, confirming logs and patches are stored and retrievable via presigned URLs.

**Acceptance Scenarios**:

1. **Given** the replacement storage is running, **When** the backend writes an execution log, **Then** the log is stored and retrievable using the same key format as before
2. **Given** the replacement storage is running, **When** the application generates a presigned URL for a stored object, **Then** the URL resolves to the correct object content
3. **Given** the replacement storage is running, **When** the application deletes an object, **Then** the object is removed and subsequent reads return a not-found response

---

### Edge Cases

- What happens if the storage service is not yet healthy when the API or worker starts? Dependent services must wait for a confirmed-healthy storage service before initialising their connections.
- What happens if the bucket already exists on container restart? Bucket creation must be idempotent — re-running `docker compose up` must not fail if the bucket was already created in a previous run.
- What happens if a stored object key does not exist? The application must receive a clear not-found error (consistent with current behaviour) rather than an ambiguous storage error.
- What happens if Docker volumes are wiped? Re-running `docker compose up` must recreate the bucket automatically without manual intervention.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The storage service MUST be open-source with a licence that does not impose copyleft restrictions on the application (e.g., Apache 2.0, LGPL, or equivalent)
- **FR-002**: The storage service MUST expose an S3-compatible API, enabling the existing `boto3`-based object store adapter to work without code changes
- **FR-003**: The storage service MUST be runnable as a single Docker container (or a minimal set of containers) suitable for local development via Docker Compose
- **FR-004**: The storage service MUST support the following S3 operations used by the application: `PutObject`, `GetObject`, `DeleteObject`, and presigned URL generation
- **FR-005**: The `docker-compose.yml` MUST be updated to replace the MinIO service and MinIO init container with the chosen replacement service and an equivalent bucket initialisation step
- **FR-006**: The replacement service MUST provide a browser-accessible management UI for inspecting buckets and objects
- **FR-007**: An initialisation step MUST automatically create the `rift-artifacts` bucket on first start; this step MUST be idempotent on subsequent starts
- **FR-008**: All environment variable names used for object storage configuration (endpoint, bucket, access key, secret key, region) MUST remain unchanged so no developer workflow changes are required
- **FR-009**: The replacement service MUST persist data across container restarts using a named Docker volume
- **FR-010**: Service health checks MUST be defined so that dependent services (API, worker) only start after the storage service is confirmed healthy

### Key Entities

- **Object Storage Service**: The Docker-based S3-compatible service that replaces MinIO; responsible for storing and serving binary blobs (execution logs, patch files) under named bucket/key paths
- **Storage Bucket (`rift-artifacts`)**: The logical container for all application objects; must exist and be ready before the API or worker attempts any read or write operation
- **Initialisation Job**: A one-time or idempotent startup task that creates the required bucket if it does not already exist; succeeds silently on repeat runs

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `docker compose up` completes with all services healthy (including the replacement storage service) within 3 minutes on a standard developer machine with no pre-existing volumes
- **SC-002**: All existing object storage operations (write log, write patch, read object, delete object, presigned URL) complete successfully with the replacement service, with zero changes to backend application code
- **SC-003**: Bucket creation is fully automated — a developer who has never run the stack before does not need to manually create the bucket or configure the storage service
- **SC-004**: The storage management UI is accessible in a browser at a documented local URL when the stack is running
- **SC-005**: `docker compose up` run a second time (with existing volumes) completes without errors — the initialisation step handles the already-existing bucket gracefully
- **SC-006**: The replacement storage service is actively maintained (last release within 12 months at time of adoption) and has no known critical security vulnerabilities in the chosen version

## Assumptions

- The application only uses the S3-compatible interface (boto3); no MinIO-specific SDK or proprietary extensions are used anywhere in the codebase — confirmed by review of `backend/src/adapters/object_store/s3_adapter.py`
- The local development stack does not need multi-region replication, erasure coding, or production-grade distributed storage; a single-node configuration is sufficient
- Presigned URL generation must work from the host machine's browser — the presigned URL host must be reachable on `localhost` (not only within the Docker network)
- The chosen replacement must not impose AGPL‑style copyleft on application code that communicates with it over the network (network use clause applicability is evaluated per tool)
- Garage is the preferred candidate due to its LGPL-3.0 licence and lightweight single-binary Docker image with native S3 API support; SeaweedFS (Apache 2.0) is an acceptable alternative

## Out of Scope

- Production-grade distributed or replicated storage configuration
- Migration or export of existing data stored in the old MinIO instance
- Changes to the backend `S3ObjectStoreAdapter` code (must remain unchanged)
- Helm chart or Kubernetes deployment updates (addressed separately)
- Performance benchmarking or load testing of the replacement service
