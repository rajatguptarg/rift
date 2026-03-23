# Tasks: Replace MinIO with SeaweedFS (Open-Source S3-Compatible Storage)

**Input**: Design documents from `/specs/002-replace-minio-storage/`
**Branch**: `002-replace-minio-storage`
**Date**: 2026-03-23

## Format: `[ID] [P?] [Story?] Description with file path`

- **[P]**: Can run in parallel (different files, no blocking dependencies)
- **[Story]**: Which user story (US1, US2, US3)

---

## Phase 1: Setup

**Purpose**: Create the SeaweedFS identity configuration file required for S3 auth.

- [X] T001 Create `infra/seaweedfs/` directory and write `infra/seaweedfs/s3-config.json` with SeaweedFS S3 identity config — credentials `minioadmin`/`minioadmin`, actions `["Read","Write","List","Tagging","Admin"]`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core docker-compose infrastructure changes that ALL user stories depend on. Must be complete before US1 can be validated.

**⚠️ CRITICAL**: No user story can be verified until these tasks are complete.

- [X] T002 Update `docker-compose.yml` — change `OBJECT_STORE_ENDPOINT` in `x-backend-env` anchor from `http://minio:9000` to `http://seaweedfs:9000`
- [X] T003 Update `docker-compose.yml` — replace the `minio` service block with a `seaweedfs` service block: image `chrislusf/seaweedfs:3.71`, command `server -s3 -s3.port=9000 -s3.config=/etc/seaweedfs/s3-config.json -filer -volume.max=100 -master.volumeSizeLimitMB=200 -ip.bind=0.0.0.0`, ports `9000:9000` (S3 API) and `8888:8888` (Filer UI), volume `seaweedfs_data:/data`, bind mount `./infra/seaweedfs/s3-config.json:/etc/seaweedfs/s3-config.json:ro`, health check on `http://localhost:9333/cluster/status`
- [X] T004 Update `docker-compose.yml` — replace the `minio-init` service block with a `storage-init` service block: image `amazon/aws-cli:2.15.37`, env vars `AWS_ACCESS_KEY_ID=minioadmin`, `AWS_SECRET_ACCESS_KEY=minioadmin`, `AWS_DEFAULT_REGION=us-east-1`, command `aws s3api create-bucket --bucket rift-artifacts --endpoint-url http://seaweedfs:9000 2>/dev/null || true`, depends_on `seaweedfs (service_healthy)`, restart `"no"`
- [X] T005 Update `docker-compose.yml` — add `storage-init` to `depends_on` of both the `api` service and the `worker` service with condition `service_completed_successfully`
- [X] T006 Update `docker-compose.yml` — rename `minio_data` to `seaweedfs_data` in the `volumes:` block at the bottom of the file; update the file header comment block (Services list: `minio` → `seaweedfs`; Access section: remove MinIO console line)

**Checkpoint**: `docker compose up --build` runs; `rift-seaweedfs` reaches healthy; `rift-storage-init` exits 0; API and worker start.

---

## Phase 3: User Story 1 — Developer Starts Full Local Stack Without Storage Errors (Priority: P1) 🎯 MVP

**Goal**: The full local stack (`docker compose up`) starts cleanly with SeaweedFS, the bucket is created automatically, and the API and worker can write and read artifacts.

**Independent Test**: Run `docker compose up --build` from a clean state (no existing volumes). Confirm `rift-storage-init` exits with code 0, `rift-api` becomes healthy, and a `PUT` then `GET` against `http://localhost:9000/rift-artifacts/test-key` using the `minioadmin` credentials succeeds.

- [X] T007 [US1] Validate that T001–T006 are complete, then run `docker compose config` to confirm no YAML syntax errors in `docker-compose.yml` — fix any issues found before proceeding
- [X] T008 [US1] Update `docker-compose.yml` header comment — add `seaweedfs` to the Services section and replace the MinIO access entry with the SeaweedFS S3 API and Filer UI entries

> **Note**: T008 is minor documentation within docker-compose.yml itself. It is listed here under US1 because the access URLs are part of US1's "stack starts correctly" story.

**Checkpoint**: US1 is fully functional. Run `docker compose up --build` and verify all health checks pass.

---

## Phase 4: User Story 2 — Developer Inspects Stored Artifacts via Web UI (Priority: P2)

**Goal**: A developer can open `http://localhost:8888` in their browser and browse the contents of the `rift-artifacts` bucket.

**Independent Test**: With the stack running, write a test artifact via the S3 API, then open `http://localhost:8888/` and navigate to `/buckets/rift-artifacts/` to confirm the object key is listed.

- [X] T009 [P] [US2] Update `README.md` — in the "Getting Started" / access URL table, replace the MinIO console row (`http://localhost:9001` / `minioadmin/minioadmin`) with the SeaweedFS Filer UI row (`http://localhost:8888`); update any prose references from "MinIO" to "SeaweedFS" in the Docker stack description
- [X] T010 [P] [US2] Update `README.md` — in the "Local Development (hot-reload)" section, update the "Starts MongoDB, Redis, Temporal, MinIO in Docker" comment to reflect SeaweedFS

**Checkpoint**: US2 is fully functional. README correctly documents the new storage service and UI URL.

---

## Phase 5: User Story 3 — Existing Application Behaviour Is Unchanged (Priority: P3)

**Goal**: All S3ObjectStoreAdapter operations (PutObject, GetObject, DeleteObject, presigned URL) work correctly against SeaweedFS. No backend code changes are required.

**Independent Test**: Run `pytest backend/tests/integration/test_s3_adapter.py -v` with the SeaweedFS stack running. All assertions pass. Run the full backend test suite and confirm no regressions.

- [X] T011 [P] [US3] Create `backend/tests/integration/test_s3_adapter.py` — integration test that instantiates `S3ObjectStoreAdapter` against `http://localhost:9000` with `minioadmin`/`minioadmin` credentials, then:
  1. Calls `put_object(key, body, content_type)` and asserts no exception
  2. Calls `get_object(key)` and asserts the returned bytes equal the original body
  3. Calls `delete_object(key)` and asserts no exception
  4. Calls `get_object(key)` again and asserts `FileNotFoundError` is raised
  5. Calls `put_log(run_id, workspace_id, log_content)` and asserts the returned key follows the `logs/<run_id>/<workspace_id>.log` pattern
  6. Calls `put_patch(run_id, workspace_id, patch)` and asserts the returned key follows the `patches/<run_id>/<workspace_id>.patch` pattern
- [X] T012 [US3] Add a `conftest.py` fixture to `backend/tests/integration/` (or update the existing one) that skips integration tests if the SeaweedFS S3 endpoint at `http://localhost:9000` is not reachable — use `pytest.mark.skipif` or a session-scoped fixture with `requests.head`

**Checkpoint**: US3 is fully functional. Integration tests pass against the running SeaweedFS stack.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation cleanup, ADR finalization, and full-stack validation.

- [X] T013 [P] Update `specs/002-replace-minio-storage/spec.md` — change `**Status**: Draft` to `**Status**: Accepted`
- [X] T014 [P] Verify `docs/adr/adr-007-seaweedfs-storage.md` exists and status is `Accepted` (created during planning phase — confirm it was committed)
- [X] T015 Run the full quickstart validation from `specs/002-replace-minio-storage/quickstart.md`: perform a clean volume wipe (`docker compose down -v`), run `docker compose up --build`, confirm all services reach healthy state, browse Filer UI at `http://localhost:8888`, run `pytest backend/tests/integration/ -v`
- [X] T016 [P] Update `backend/src/core/config.py` — change the default value comments for `object_store_access_key` and `object_store_secret_key` if they contain any MinIO-specific wording; update `object_store_endpoint` default from `http://localhost:9000` to `http://localhost:9000` (value is already correct — verify and leave unchanged, or update any inline comment referring to MinIO)

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup)
    └──▶ Phase 2 (Foundational docker-compose changes)
              ├──▶ Phase 3 (US1 - stack validation)
              ├──▶ Phase 4 (US2 - README docs) [can run in parallel with Phase 3]
              └──▶ Phase 5 (US3 - integration tests) [can run in parallel with Phase 3/4]
                        └──▶ Phase 6 (Polish)
```

### User Story Dependencies

- **US1 (P1)**: Requires Phase 2 complete. No dependency on US2 or US3.
- **US2 (P2)**: Requires Phase 2 complete (port 8888 exposed by seaweedfs service). Can run alongside US1.
- **US3 (P3)**: Requires Phase 2 complete (SeaweedFS running). Can run alongside US1/US2. Integration test requires stack to be up.

### Within Each Story

- T001 must precede T003 (s3-config.json must exist before seaweedfs service is defined)
- T002–T006 modify the same file (`docker-compose.yml`) — execute sequentially in order
- T007 validates the complete docker-compose change — must follow T001–T006
- T009, T010, T011, T012도, T013, T014, T016 can all run in parallel after Phase 2

### Parallel Opportunities

After T001–T006 are committed:

```
Branch A (US1): T007, T008
Branch B (US2): T009, T010             [parallel with Branch A]
Branch C (US3): T011, T012             [parallel with Branch A/B]
Branch D (Docs): T013, T014, T016      [parallel with Branch A/B/C]
```

Then T015 (full integration validation) runs last.

---

## Implementation Strategy

**MVP Scope** (minimum to unblock development): Phases 1 + 2 + Phase 3 = T001–T008

This delivers US1: the stack starts without errors, the bucket is created, and the API/worker connect to SeaweedFS. US2 (web UI docs) and US3 (integration tests) can follow.

**Suggested commit sequence:**
1. `feat(infra): add SeaweedFS identity config [RIFT-002]` — T001
2. `feat(infra): replace MinIO with SeaweedFS in docker-compose [RIFT-002]` — T002–T008
3. `docs(readme): update storage service references to SeaweedFS [RIFT-002]` — T009–T010
4. `test(integration): add S3ObjectStoreAdapter integration test [RIFT-002]` — T011–T012
5. `docs(adr): finalize ADR-007 and spec status [RIFT-002]` — T013–T016
