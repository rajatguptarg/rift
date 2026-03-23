# Implementation Plan: Rift Batch Changes Platform

**Branch**: `001-batch-changes-platform` | **Date**: 2026-03-23 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-batch-changes-platform/spec.md`

## Summary

Build the Rift Batch Changes platform — a declarative control plane with an ephemeral execution plane that enables engineering teams to create, preview, publish, and track large-scale code changes across thousands of repositories via a single YAML spec. The backend is Python/FastAPI with MongoDB persistence, Redis caching, and Temporal-driven workflow orchestration. The frontend is React/TypeScript. Containerized workspace execution runs on Kubernetes Jobs. A desired-state reconciliation loop keeps code host reality (PRs/MRs) aligned with internal changeset specs.

## Technical Context

**Language/Version**: Python 3.12 (backend), TypeScript 5.x (frontend/CLI)
**Primary Dependencies**: FastAPI, Pydantic, Motor (async MongoDB driver), Temporal Python SDK, React 18, React Router, TanStack Query
**Storage**: MongoDB (primary), Redis (cache + coordination), S3-compatible object storage (logs/patches)
**Testing**: pytest + pytest-asyncio + pytest-cov (backend), Vitest + React Testing Library (frontend), Playwright (functional)
**Target Platform**: Kubernetes (Linux containers), single-region active/passive
**Project Type**: web-service (backend API + frontend SPA + CLI + async workers)
**Performance Goals**: API p95 < 200ms, preview start < 60s, dashboard load < 2s p95, webhook-to-UI freshness < 30s p95
**Constraints**: 99.9% API availability, code host rate limit compliance, runner isolation (non-root, no docker socket, egress deny-by-default)
**Scale/Scope**: 5,000 repos per batch change, 25,000 workspace executions/day, 500 concurrent runners

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| # | Principle | Status | Evidence |
|---|-----------|--------|----------|
| I | Test Coverage ≥80% (NON-NEGOTIABLE) | ✅ PASS | Plan includes unit/integration/functional test layers; CI gate enforces ≥80% coverage |
| II | Testing Pyramid (Unit → Integration → Functional) | ✅ PASS | Backend: pytest unit + integration (Motor/testcontainers) + functional (Playwright). Frontend: Vitest unit + integration + Playwright e2e |
| III | Secret Management (.env + env vars) | ✅ PASS | .env for local dev, .env.example committed, KMS-backed envelope encryption for credentials, Kubernetes Secrets for prod |
| IV | Documentation Currency | ✅ PASS | OpenAPI spec auto-generated from Pydantic models; docs updated in same PR as code |
| V | README Completeness (7 sections) | ✅ PASS | README structure planned with all 7 required sections |
| VI | ADRs under docs/adr/ | ✅ PASS | ADR directory exists; key decisions (MongoDB, Temporal, REST vs GraphQL) will be recorded |

**Gate result: PASS — no violations. Proceeding to Phase 0.**

## Project Structure

### Documentation (this feature)

```text
specs/001-batch-changes-platform/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── api.yaml         # OpenAPI 3.1 spec
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── api/                    # FastAPI routers and middleware
│   │   ├── routes/             # Route modules (batch_changes, changesets, credentials, templates, etc.)
│   │   ├── middleware/         # Auth, redaction, error handling
│   │   └── dependencies.py    # FastAPI dependency injection
│   ├── models/                 # Pydantic models (request/response + domain)
│   │   ├── batch_change.py
│   │   ├── batch_spec.py
│   │   ├── changeset.py
│   │   ├── changeset_spec.py
│   │   ├── credential.py
│   │   ├── execution.py
│   │   ├── template.py
│   │   └── namespace.py
│   ├── services/               # Business logic layer
│   │   ├── batch_change_service.py
│   │   ├── execution_orchestrator.py
│   │   ├── changeset_controller.py
│   │   ├── credential_service.py
│   │   ├── template_service.py
│   │   └── analytics_service.py
│   ├── adapters/               # External integrations
│   │   ├── code_hosts/         # GitHub, GitLab, Bitbucket, Gerrit adapters
│   │   ├── mongo/              # MongoDB repositories (data access)
│   │   ├── redis/              # Redis cache and coordination
│   │   ├── object_store/       # S3-compatible artifact storage
│   │   └── search/             # Repo search/mirror adapter
│   ├── workflows/              # Temporal workflow and activity definitions
│   │   ├── preview_workflow.py
│   │   ├── apply_workflow.py
│   │   └── activities/
│   ├── core/                   # Config, logging, encryption, errors
│   │   ├── config.py
│   │   ├── encryption.py
│   │   ├── logging.py
│   │   └── errors.py
│   └── main.py                 # FastAPI app entrypoint
├── tests/
│   ├── unit/                   # Isolated logic tests
│   ├── integration/            # Service + DB/cache tests
│   └── functional/             # End-to-end API + workflow tests
├── pyproject.toml
├── Dockerfile
└── .env.example

frontend/
├── src/
│   ├── components/             # Shared UI components
│   ├── pages/                  # Route-level page components
│   │   ├── BatchChangesList/
│   │   ├── BatchChangeCreate/
│   │   ├── BatchSpecEditor/
│   │   ├── ExecutionView/
│   │   ├── ChangesetDashboard/
│   │   └── CredentialSettings/
│   ├── services/               # API client layer
│   ├── hooks/                  # Custom React hooks
│   ├── types/                  # TypeScript type definitions
│   └── App.tsx
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/                    # Playwright tests
├── package.json
├── tsconfig.json
├── vite.config.ts
└── Dockerfile

cli/
├── src/                        # rift CLI source (TypeScript/Node)
│   ├── commands/
│   │   ├── login.ts
│   │   ├── batch-preview.ts
│   │   └── batch-apply.ts
│   ├── client/                 # API client
│   └── index.ts
├── tests/
├── package.json
└── tsconfig.json

helm/
├── Chart.yaml
├── values.yaml
└── charts/
    ├── frontend/
    ├── api/
    ├── workers/
    ├── runners/
    └── ingress/

docs/
├── adr/
├── product/
│   ├── PRD.md
│   └── HLD.md
└── design/

.github/
└── workflows/
    ├── ci-backend.yml
    ├── ci-frontend.yml
    ├── ci-helm.yml
    ├── cd-staging.yml
    └── cd-production.yml
```

**Structure Decision**: Web application layout (backend + frontend + CLI) selected based on the HLD's service-oriented architecture. Backend follows a layered architecture (API → Services → Adapters) with Temporal workflows as the orchestration layer. Frontend is a standalone React SPA. CLI is a separate TypeScript package sharing API contracts with the frontend.

## Complexity Tracking

> No constitution violations — this section is N/A.

## Constitution Re-Check (Post Phase 1 Design)

*GATE: Re-evaluated after Phase 1 design artifacts are complete.*

| # | Principle | Status | Post-Design Evidence |
|---|-----------|--------|---------------------|
| I | Test Coverage ≥80% (NON-NEGOTIABLE) | ✅ PASS | quickstart.md documents `pytest --cov-fail-under=80`; three test layers in project structure |
| II | Testing Pyramid | ✅ PASS | Unit (Pydantic models, state machines), Integration (Motor + testcontainers), Functional (Playwright) |
| III | Secret Management | ✅ PASS | Credential entity uses KMS envelope encryption; `.env` + `.env.example` in quickstart; no secrets in contracts |
| IV | Documentation Currency | ✅ PASS | contracts/api.yaml is OpenAPI source of truth; auto-generated from Pydantic models |
| V | README Completeness | ✅ PASS | quickstart.md covers all 7 required README sections |
| VI | ADRs | ✅ PASS | research.md documents 13 decisions ready for ADR conversion during implementation |

**Post-design gate result: PASS — proceeding to task generation.**
