# Tasks: Rift Batch Changes Platform

**Input**: Design documents from `/specs/001-batch-changes-platform/`
**Prerequisites**: plan.md (loaded), spec.md (loaded), research.md (loaded), data-model.md (loaded), contracts/api.yaml (loaded), quickstart.md (loaded)

**Tests**: Not explicitly requested in the feature specification. Test tasks are omitted. Tests should be added per the constitution (≥80% coverage) during implementation.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `backend/src/`, `backend/tests/`
- **Frontend**: `frontend/src/`, `frontend/tests/`
- **CLI**: `cli/src/`, `cli/tests/`
- **Infrastructure**: `helm/`, `.github/workflows/`, `docker-compose.yml`
- **Docs**: `docs/adr/`, `README.md`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, tooling, and local dev environment

- [ ] T001 Create root project directory structure per plan.md (backend/, frontend/, cli/, helm/, docs/adr/, .github/workflows/)
- [ ] T002 Initialize backend Python project with FastAPI, Pydantic, Motor, Temporal SDK dependencies in backend/pyproject.toml
- [ ] T003 [P] Initialize frontend React 18 + TypeScript 5.x project with Vite, TanStack Query, React Router in frontend/package.json
- [ ] T004 [P] Initialize CLI TypeScript project with commander and node-fetch in cli/package.json
- [ ] T005 [P] Create Docker Compose file for MongoDB, Redis, and Temporal dev server in docker-compose.yml
- [ ] T006 [P] Create environment variable template with all required config vars in .env.example
- [ ] T007 [P] Create root Makefile with lint, test, format, and dev start commands in Makefile

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Backend Core

- [ ] T008 Implement application config module with Pydantic Settings model in backend/src/core/config.py
- [ ] T009 [P] Implement structured logging with correlation ID injection in backend/src/core/logging.py
- [ ] T010 [P] Implement domain error types and FastAPI exception handlers in backend/src/core/errors.py
- [ ] T011 Implement async MongoDB connection manager using Motor in backend/src/adapters/mongo/client.py
- [ ] T012 [P] Implement async Redis connection manager in backend/src/adapters/redis/client.py

### Backend Shared Models

- [ ] T013 [P] Implement shared Pydantic schemas (pagination, cursor, error response, common enums) in backend/src/models/common.py
- [ ] T014 Implement User domain model in backend/src/models/user.py
- [ ] T015 [P] Implement Organization domain model in backend/src/models/organization.py
- [ ] T016 Implement Namespace domain model (USER/ORG kind, visibility policy) in backend/src/models/namespace.py
- [ ] T017 [P] Implement CodeHost domain model (GITHUB, GITLAB, BITBUCKET_SERVER, BITBUCKET_CLOUD, GERRIT) in backend/src/models/code_host.py
- [ ] T018 [P] Implement Repository domain model in backend/src/models/repository.py

### Backend Data Access & Middleware

- [ ] T019 Implement base MongoDB repository pattern with optimistic concurrency in backend/src/adapters/mongo/base_repository.py
- [ ] T020 Implement auth middleware with JWT/token validation in backend/src/api/middleware/auth.py
- [ ] T021 [P] Implement redaction middleware for repository access checks in backend/src/api/middleware/redaction.py
- [ ] T022 Implement FastAPI dependency injection (db, redis, current user, namespace) in backend/src/api/dependencies.py
- [ ] T023 Create FastAPI app entrypoint with CORS, middleware, and router registration in backend/src/main.py

### Backend External Adapters

- [ ] T024 [P] Implement S3-compatible object storage adapter for logs and patches in backend/src/adapters/object_store/s3_adapter.py
- [ ] T025 Implement CodeHostAdapter base interface (Strategy pattern) in backend/src/adapters/code_hosts/base.py
- [ ] T026 Implement GitHub code host adapter in backend/src/adapters/code_hosts/github.py
- [ ] T027 [P] Implement GitLab code host adapter in backend/src/adapters/code_hosts/gitlab.py
- [ ] T028 Setup Temporal worker entrypoint and task queue config in backend/src/workflows/worker.py

### Frontend Foundation

- [ ] T029 Setup frontend app shell with React Router route definitions in frontend/src/App.tsx
- [ ] T030 [P] Implement typed API client service with TanStack Query integration in frontend/src/services/api.ts
- [ ] T031 [P] Implement auth context provider and useAuth hook in frontend/src/hooks/useAuth.ts
- [ ] T032 [P] Create shared TypeScript type definitions from API contract in frontend/src/types/api.ts

**Checkpoint**: Foundation ready — user story implementation can now begin in parallel

---

## Phase 3: User Story 1 — Create and Execute a Batch Change via Web UI (Priority: P1) 🎯 MVP

**Goal**: Users can create a batch change (from scratch or template), edit the batch spec, run a preview with real-time per-workspace execution, review diffs, and apply to finalize — all from the web UI.

**Independent Test**: Create a batch change, run preview against test repos, verify execution logs stream in real-time, review diffs, apply, and confirm changesets appear on the dashboard.

**FRs**: FR-001 (batch spec YAML), FR-002 (resolve search query), FR-003 (isolated execution), FR-004 (combine diffs + template → changeset specs), FR-005 (server-side execution), FR-007 (preview workflow), FR-008 (apply workflow), FR-016 (filtering), FR-022 (monorepo workspaces), FR-025 (execution logging), FR-026 (skip-errors), FR-027 (conflict detection)

### Backend Models

- [ ] T033 [P] [US1] Implement BatchChange domain model with state machine (DRAFT→PREVIEW_RUNNING→PREVIEW_READY→APPLYING→ACTIVE→PAUSED→ARCHIVED→FAILED) in backend/src/models/batch_change.py
- [ ] T034 [P] [US1] Implement BatchSpec domain model with YAML hash dedup in backend/src/models/batch_spec.py
- [ ] T035 [P] [US1] Implement BatchRun, WorkspaceExecution, and ExecutionStep models in backend/src/models/execution.py

### Backend Data Access

- [ ] T036 [US1] Implement BatchChange MongoDB repository with state filter queries in backend/src/adapters/mongo/batch_change_repo.py
- [ ] T037 [P] [US1] Implement BatchSpec MongoDB repository in backend/src/adapters/mongo/batch_spec_repo.py
- [ ] T038 [P] [US1] Implement BatchRun MongoDB repository in backend/src/adapters/mongo/batch_run_repo.py
- [ ] T039 [P] [US1] Implement WorkspaceExecution MongoDB repository with batch_run index in backend/src/adapters/mongo/workspace_execution_repo.py

### Backend Services

- [ ] T040 [US1] Implement BatchChangeService (create, update spec, close, archive, state transitions) in backend/src/services/batch_change_service.py
- [ ] T041 [US1] Implement ExecutionOrchestrator (trigger preview/apply, coordinate fan-out, aggregate results) in backend/src/services/execution_orchestrator.py

### Backend Workflows

- [ ] T042 [US1] Implement preview Temporal workflow with fan-out workspace execution and fan-in result aggregation in backend/src/workflows/preview_workflow.py
- [ ] T043 [US1] Implement apply Temporal workflow (finalize batch change, produce changeset specs) in backend/src/workflows/apply_workflow.py
- [ ] T044 [P] [US1] Implement workspace runner Temporal activities (clone, execute steps, capture diffs) in backend/src/workflows/activities/workspace_runner.py

### Backend API Routes

- [ ] T045 [US1] Implement batch-changes API routes (list, create, get, update spec, preview, apply, close, archive) in backend/src/api/routes/batch_changes.py
- [ ] T046 [US1] Implement batch-runs API routes (get detail, exclude workspace) in backend/src/api/routes/batch_runs.py
- [ ] T047 [US1] Implement SSE stream endpoint for live batch run updates in backend/src/api/routes/streams.py

### Frontend Pages

- [ ] T048 [P] [US1] Create BatchChangesList page with state filters and pagination in frontend/src/pages/BatchChangesList/index.tsx
- [ ] T049 [P] [US1] Create BatchChangeCreate page with name, namespace, and spec input in frontend/src/pages/BatchChangeCreate/index.tsx
- [ ] T050 [US1] Create BatchSpecEditor page with YAML editor and repository preview panel in frontend/src/pages/BatchSpecEditor/index.tsx
- [ ] T051 [US1] Create ExecutionView page with real-time per-workspace logs, step diffs, and timeline in frontend/src/pages/ExecutionView/index.tsx
- [ ] T052 [US1] Implement useExecutionStream SSE hook for live execution updates in frontend/src/hooks/useExecutionStream.ts

**Checkpoint**: User Story 1 is fully functional — users can create, preview, and apply batch changes via the web UI

---

## Phase 4: User Story 2 — Publish and Track Changesets (Priority: P1)

**Goal**: Users can publish changesets to code hosts (full PR, draft, push-only), track CI/review/merge status in near-real-time on the dashboard, and view burndown progress.

**Independent Test**: Publish changesets from an applied batch change, verify PRs appear on the code host, confirm dashboard reflects CI/review/merge status within 60 seconds, view burndown chart data.

**FRs**: FR-009 (publish modes), FR-010 (bulk actions), FR-011 (changeset state tracking), FR-012 (CI check state), FR-013 (review state), FR-014 (burndown chart), FR-015 (aggregate stats), FR-017 (reconciliation loop)

### Backend Models

- [ ] T053 [P] [US2] Implement ChangesetSpec domain model with state machine (UNPUBLISHED→PUBLISHING→PUBLISHED→MERGED/CLOSED/ARCHIVED) in backend/src/models/changeset_spec.py
- [ ] T054 [P] [US2] Implement Changeset and ChangesetEvent domain models in backend/src/models/changeset.py
- [ ] T055 [P] [US2] Implement BatchChangeStats and BurndownDaily read models in backend/src/models/analytics.py

### Backend Data Access

- [ ] T056 [US2] Implement ChangesetSpec MongoDB repository with batch_change + repo compound index in backend/src/adapters/mongo/changeset_spec_repo.py
- [ ] T057 [P] [US2] Implement Changeset MongoDB repository with state/review/check filter queries in backend/src/adapters/mongo/changeset_repo.py
- [ ] T058 [P] [US2] Implement ChangesetEvent MongoDB repository in backend/src/adapters/mongo/changeset_event_repo.py

### Backend Services

- [ ] T059 [US2] Implement ChangesetController service (publish, bulk close/archive, status sync from code host) in backend/src/services/changeset_controller.py
- [ ] T060 [US2] Implement reconciliation loop service (desired-state convergence using spec fingerprints) in backend/src/services/reconciliation_service.py
- [ ] T061 [US2] Implement code host webhook receiver (CI, review, merge events) in backend/src/api/routes/webhooks.py
- [ ] T062 [US2] Implement AnalyticsService (stats projection rebuild, daily burndown computation) in backend/src/services/analytics_service.py

### Backend API Routes

- [ ] T063 [US2] Implement changesets API routes (list with filters, publish, stats, burndown) in backend/src/api/routes/changesets.py

### Frontend Pages

- [ ] T064 [US2] Create ChangesetDashboard page with state/review/CI filters and status columns in frontend/src/pages/ChangesetDashboard/index.tsx
- [ ] T065 [US2] Implement BurndownChart component with daily data visualization in frontend/src/components/BurndownChart.tsx
- [ ] T066 [US2] Implement ChangesetBulkActions component (publish, close, archive selections) in frontend/src/components/ChangesetBulkActions.tsx

**Checkpoint**: User Stories 1 AND 2 are complete — the full core loop (create → execute → apply → publish → track) works end-to-end

---

## Phase 5: User Story 3 — Create and Execute a Batch Change via CLI (Priority: P2)

**Goal**: Power users and CI pipelines can preview and apply batch changes from the command line using `rift batch preview` and `rift batch apply`.

**Independent Test**: Run `rift batch preview -f spec.yaml` against test repos, verify preview URL works and diffs are correct as json output, then run `rift batch apply` and confirm changesets are created.

**FRs**: FR-006 (CLI preview/apply), FR-026 (--skip-errors)

- [ ] T067 [US3] Implement CLI API client with auth token storage and refresh in cli/src/client/api.ts
- [ ] T068 [US3] Implement login command with token persistence in cli/src/commands/login.ts
- [ ] T069 [US3] Implement batch preview command (resolve repos, compute diffs, print preview URL) in cli/src/commands/batch-preview.ts
- [ ] T070 [US3] Implement batch apply command with --skip-errors and --namespace flags in cli/src/commands/batch-apply.ts
- [ ] T071 [US3] Create CLI entry point with commander argument parser in cli/src/index.ts

**Checkpoint**: User Story 3 is functional — CLI users can preview and apply batch changes

---

## Phase 6: User Story 4 — Manage Credentials and Access Control (Priority: P2)

**Goal**: Site admins can manage global credentials, users can add personal tokens, and repository access control with redaction is enforced.

**Independent Test**: Configure global and per-user credentials, run a batch change using each credential type, verify unauthorized users see redacted repository names and diffs.

**FRs**: FR-019 (credential storage), FR-020 (namespace-based access), FR-021 (redaction)

- [ ] T072 [P] [US4] Implement Credential domain model with encryption fields in backend/src/models/credential.py
- [ ] T073 [US4] Implement KMS envelope encryption module (encrypt, decrypt, key rotation) in backend/src/core/encryption.py
- [ ] T074 [US4] Implement CredentialService (CRUD, scope resolution per namespace/user/global) in backend/src/services/credential_service.py
- [ ] T075 [US4] Implement credentials API routes (list, create, delete) with token redaction in backend/src/api/routes/credentials.py
- [ ] T076 [US4] Enforce namespace-scoped access control rules in auth middleware in backend/src/api/middleware/auth.py
- [ ] T077 [US4] Create CredentialSettings page with code host credential management UI in frontend/src/pages/CredentialSettings/index.tsx

**Checkpoint**: User Story 4 is functional — credentials and RBAC are enforced

---

## Phase 7: User Story 5 — Use Templates for Common Batch Changes (Priority: P3)

**Goal**: Admins can create reusable batch spec templates with form fields, and users can select templates during batch change creation with regex-validated input.

**Independent Test**: Create a template with validated fields, select it during batch change creation, verify form validation works, confirm generated YAML matches template with substituted parameters.

**FRs**: FR-023 (template library with regex validation)

- [ ] T078 [P] [US5] Implement Template domain model with form schema and validation rules in backend/src/models/template.py
- [ ] T079 [US5] Implement TemplateService with YAML parameter substitution and validation in backend/src/services/template_service.py
- [ ] T080 [US5] Implement templates API routes (list, create) in backend/src/api/routes/templates.py
- [ ] T081 [US5] Add template selection step to BatchChangeCreate page in frontend/src/pages/BatchChangeCreate/index.tsx
- [ ] T082 [US5] Implement TemplateForm component with dynamic fields and regex validation in frontend/src/components/TemplateForm.tsx

**Checkpoint**: User Story 5 is functional — template-driven batch change creation works

---

## Phase 8: User Story 6 — Track Manually-Created Changesets (Priority: P3)

**Goal**: Users can import externally-created PRs/MRs into a batch change for unified tracking on the dashboard and burndown chart.

**Independent Test**: Import known existing PRs into a batch change, verify dashboard reflects their CI/review/merge status, confirm burndown includes imported changesets.

**FRs**: FR-024 (import external changesets)

- [ ] T083 [US6] Implement changeset import logic (resolve external URLs, create tracking records) in backend/src/services/changeset_controller.py
- [ ] T084 [US6] Implement import changesets API route in backend/src/api/routes/changesets.py
- [ ] T085 [US6] Add changeset import UI (URL input, import button) to ChangesetDashboard in frontend/src/pages/ChangesetDashboard/index.tsx

**Checkpoint**: User Story 6 is functional — external changesets are tracked alongside Rift-created ones

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Audit logging, CI/CD, deployment, documentation, and validation

### Audit Infrastructure

- [ ] T086 [P] Implement AuditEvent model and MongoDB repository in backend/src/models/audit.py
- [ ] T087 Implement audit logging service (intercept state changes across all resources) in backend/src/services/audit_service.py
- [ ] T088 Implement audit-events API route (list with filters) in backend/src/api/routes/audit.py

### CI/CD & Deployment

- [ ] T089 [P] Create CI backend workflow (lint, test, coverage ≥80% gate) in .github/workflows/ci-backend.yml
- [ ] T090 [P] Create CI frontend workflow (lint, test, coverage gate) in .github/workflows/ci-frontend.yml
- [ ] T091 [P] Create Helm umbrella chart with subcharts (frontend, api, workers, runners, ingress) in helm/Chart.yaml

### Documentation

- [ ] T092 Update project README with architecture overview, setup, testing, and contribution guide in README.md
- [ ] T093 Create ADR for MongoDB as primary data store in docs/adr/adr-001-mongodb-primary-store.md
- [ ] T094 [P] Create ADR for Temporal workflow orchestration in docs/adr/adr-002-temporal-orchestration.md
- [ ] T095 [P] Create ADR for REST+SSE API style over GraphQL in docs/adr/adr-003-rest-sse-api-style.md

### Validation

- [ ] T096 Run quickstart.md end-to-end validation (full local dev setup and smoke test)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — **BLOCKS all user stories**
- **US1 (Phase 3)**: Depends on Foundational (Phase 2) — no dependency on other stories
- **US2 (Phase 4)**: Depends on Foundational (Phase 2) — integrates with US1 changeset specs produced by apply workflow
- **US3 (Phase 5)**: Depends on Foundational (Phase 2) — reuses US1 backend API routes
- **US4 (Phase 6)**: Depends on Foundational (Phase 2) — integrates with auth middleware from Phase 2
- **US5 (Phase 7)**: Depends on Foundational (Phase 2) — integrates with US1 batch change creation flow
- **US6 (Phase 8)**: Depends on US2 (Phase 4) — requires changeset tracking infrastructure
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

```
Phase 1 (Setup) → Phase 2 (Foundational) → ┬→ Phase 3 (US1: Create/Execute) ──┐
                                            ├→ Phase 4 (US2: Publish/Track) ───┤
                                            ├→ Phase 5 (US3: CLI) ─────────────┤
                                            ├→ Phase 6 (US4: Credentials) ─────┤
                                            └→ Phase 7 (US5: Templates) ───────┤
                                                                               │
                              Phase 4 (US2) → Phase 8 (US6: Import) ───────────┤
                                                                               │
                                                   Phase 9 (Polish) ◄──────────┘
```

### Within Each User Story

1. Models before data access repositories
2. Data access before services
3. Services before API routes
4. API routes before frontend pages
5. Core implementation before integration

### Parallel Opportunities

**Phase 1**: T003, T004, T005, T006, T007 can all run in parallel after T001+T002
**Phase 2**: T009+T010 parallel; T012 parallel with T011; T013-T018 model tasks with [P] parallel; T024+T027 parallel with T025+T026; T030+T031+T032 parallel
**Phase 3**: T033+T034+T035 (models) parallel; T037+T038+T039 (repos) parallel; T048+T049 (pages) parallel
**Phase 4**: T053+T054+T055 (models) parallel; T057+T058 (repos) parallel
**Phase 6**: T072 parallel with other non-dependent tasks
**Phase 9**: T089+T090+T091 parallel; T093+T094+T095 parallel

---

## Parallel Example: User Story 1

```bash
# Step 1: Launch all US1 models in parallel:
Task T033: "Implement BatchChange domain model in backend/src/models/batch_change.py"
Task T034: "Implement BatchSpec domain model in backend/src/models/batch_spec.py"
Task T035: "Implement BatchRun, WorkspaceExecution, ExecutionStep models in backend/src/models/execution.py"

# Step 2: Launch all US1 repositories in parallel (after models):
Task T036: "Implement BatchChange MongoDB repository in backend/src/adapters/mongo/batch_change_repo.py"
Task T037: "Implement BatchSpec MongoDB repository in backend/src/adapters/mongo/batch_spec_repo.py"
Task T038: "Implement BatchRun MongoDB repository in backend/src/adapters/mongo/batch_run_repo.py"
Task T039: "Implement WorkspaceExecution MongoDB repository in backend/src/adapters/mongo/workspace_execution_repo.py"

# Step 3: Services (sequential, depends on repos):
Task T040: "Implement BatchChangeService"
Task T041: "Implement ExecutionOrchestrator"

# Step 4: Workflows + activities in parallel:
Task T042: "Implement preview Temporal workflow"
Task T043: "Implement apply Temporal workflow"
Task T044: "Implement workspace runner activities" (parallel with T042/T043)

# Step 5: API routes (sequential, depends on services):
Task T045: "Implement batch-changes API routes"
Task T046: "Implement batch-runs API routes"
Task T047: "Implement SSE stream endpoint"

# Step 6: Frontend pages (partially parallel):
Task T048: "Create BatchChangesList page" (parallel with T049)
Task T049: "Create BatchChangeCreate page" (parallel with T048)
Task T050: "Create BatchSpecEditor page"
Task T051: "Create ExecutionView page"
Task T052: "Implement useExecutionStream SSE hook" (before T051 integration)
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL — blocks all stories)
3. Complete Phase 3: User Story 1 (create, preview, apply)
4. **STOP and VALIDATE**: Test US1 independently
5. Complete Phase 4: User Story 2 (publish, track, reconcile)
6. **STOP and VALIDATE**: Full core loop works end-to-end
7. Deploy/demo if ready — this is the MVP

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 → Create/Execute works → First demo
3. Add US2 → Full core loop → **MVP ship** 🚀
4. Add US3 → CLI access → Power user/CI enablement
5. Add US4 → Credentials/RBAC → Enterprise readiness
6. Add US5 → Templates → Adoption acceleration
7. Add US6 → Import → Migration support
8. Polish → CI/CD, Helm, ADRs, README → Production readiness

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (backend)
   - Developer B: User Story 1 (frontend) — starts after API routes
   - Developer C: User Story 4 (credentials/RBAC) — independent
3. After US1 is done:
   - Developer A: User Story 2 (backend)
   - Developer B: User Story 2 (frontend)
   - Developer C: User Story 3 (CLI)
4. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Tests should be written during implementation per constitution (≥80% coverage gate)
- 96 total tasks across 9 phases
