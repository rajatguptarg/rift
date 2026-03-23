# Research: Rift Batch Changes Platform

**Date**: 2026-03-23
**Source**: HLD.md technology choices, PRD requirements, constitution principles

## 1. Backend Framework

- **Decision**: FastAPI (Python 3.12)
- **Rationale**: Async-first, native Pydantic validation, automatic OpenAPI generation, strong ecosystem for background workers. Aligns with constitution principle IV (documentation currency — OpenAPI auto-generated from code).
- **Alternatives considered**:
  - Django REST Framework — heavier, sync-first, less natural for SSE/WebSocket
  - Go + Chi — faster runtime but higher development cost, smaller team familiarity
  - Node/Express — weaker type validation story compared to Pydantic

## 2. Primary Database

- **Decision**: MongoDB
- **Rationale**: Document-oriented model fits batch change aggregates naturally (nested specs, execution results, changeset events). Flexible schema supports evolving entities during MVP. Horizontal scaling via sharding when needed.
- **Alternatives considered**:
  - PostgreSQL — strong ACID but requires ORM overhead for deeply nested documents; JSON columns lose query ergonomics
  - DynamoDB — vendor lock-in, complex secondary access patterns for dashboard queries

## 3. Cache and Coordination

- **Decision**: Redis
- **Rationale**: Proven for distributed rate-limit counters, permission check caching, dashboard summary caching, and SSE pub/sub. Sub-millisecond reads for hot paths (changeset pages, permission checks).
- **Alternatives considered**:
  - Memcached — no pub/sub, no atomic counters
  - Application-level in-memory cache — no distribution across API pods

## 4. Workflow Orchestration

- **Decision**: Temporal (Python SDK)
- **Rationale**: Native support for fan-out/fan-in (preview/apply workflows with thousands of workspace executions), built-in retry policies, workflow visibility, and crash recovery. Temporal's deterministic replay model ensures workspace executions resume after worker restarts without duplicate work.
- **Alternatives considered**:
  - Celery + Redis — limited workflow primitives, no native fan-out/fan-in, manual state management
  - Apache Airflow — DAG-oriented, not suited for dynamic per-request workflow generation
  - Custom queue + state machine — high development cost, reinvents Temporal features

## 5. Container Execution

- **Decision**: Kubernetes Jobs managed by Runner Manager
- **Rationale**: One Job per workspace execution provides isolation (non-root, egress deny, CPU/memory quotas). K8s native scheduling handles concurrency budget. TTL cleanup reaps stuck jobs.
- **Alternatives considered**:
  - Docker-in-Docker — security risk (Docker socket exposure), complex networking
  - AWS Fargate / Cloud Run — vendor lock-in, less control over network policies
  - Bare process execution — no isolation, security risk

## 6. Frontend

- **Decision**: React 18 + TypeScript + Vite
- **Rationale**: Component-based architecture suits the complex dashboard UI (changeset tables, burndown charts, diff viewers, real-time status). TanStack Query for server state management. Vite for fast HMR during development.
- **Alternatives considered**:
  - Next.js — SSR not needed for an authenticated internal tool
  - Vue — smaller ecosystem for enterprise-grade diff viewers and code editors
  - Svelte — smaller component library ecosystem

## 7. API Style

- **Decision**: REST + Server-Sent Events (SSE)
- **Rationale**: REST is simpler to implement in FastAPI, easier for CLI consumption, and well-supported by code generation tools. SSE provides real-time execution updates without WebSocket complexity. OpenAPI spec auto-generated from Pydantic models satisfies constitution principle IV.
- **Alternatives considered**:
  - GraphQL — flexible querying but higher implementation complexity, harder to cache, overkill for MVP
  - gRPC — fast but poor browser support without grpc-web proxy

## 8. Credential Security

- **Decision**: KMS-backed envelope encryption
- **Rationale**: Data keys encrypted by cloud KMS, token ciphertext stored in MongoDB. Tokens decrypted in-memory only, injected as short-lived env vars into runners. Secret scanning on logs/artifacts before persistence. Aligns with constitution principle III (secrets never in version control or logs).
- **Alternatives considered**:
  - HashiCorp Vault — additional infrastructure dependency for MVP
  - Application-level AES — no key rotation audit trail, no hardware security boundary

## 9. Observability

- **Decision**: OpenTelemetry + Prometheus-compatible metrics + structured logging
- **Rationale**: Vendor-neutral telemetry. Distributed tracing from React → FastAPI → Temporal → Runner → Controller. Structured logs with correlation IDs (batch_change_id, batch_run_id, workspace_execution_id).
- **Alternatives considered**:
  - Datadog-native — vendor lock-in
  - ELK-only — no native tracing

## 10. CI/CD

- **Decision**: GitHub Actions with reusable workflows
- **Rationale**: Native to the project's code host. Reusable workflows for shared build steps. Environment protection rules for production deployments. Concurrency groups prevent overlapping deploys.
- **Alternatives considered**:
  - Jenkins — higher operational overhead
  - GitLab CI — project hosted on GitHub

## 11. Deployment

- **Decision**: Kubernetes + Helm charts
- **Rationale**: Umbrella chart with subcharts for frontend, API, workers, runners, and ingress. Network policies enforce private-only access to MongoDB, Redis, Temporal. Separate namespaces (rift-frontend, rift-api, rift-workers, rift-runners).
- **Alternatives considered**:
  - Docker Compose — insufficient for production runner isolation and scaling
  - Serverless (Lambda) — incompatible with long-running Temporal workers and stateful reconciliation loops

## 12. Testing Strategy

- **Decision**: Three-layer testing pyramid per constitution principles I and II
- **Rationale**:
  - **Unit tests** (pytest / Vitest): Isolated business logic, Pydantic model validation, state machine transitions, template rendering. Largest test count.
  - **Integration tests** (pytest + testcontainers / Vitest + MSW): Service layer with real MongoDB/Redis, code host adapter mocks, Temporal test server.
  - **Functional tests** (Playwright): End-to-end user journeys — create batch change, execute, publish, track on dashboard.
- **Coverage target**: ≥80% combined (enforced in CI).

## 13. Code Host Adapter Pattern

- **Decision**: Strategy pattern with a common `CodeHostAdapter` interface
- **Rationale**: Each code host (GitHub, GitLab, Bitbucket, Gerrit) implements the same interface (create_branch, create_pr, get_pr_status, push_branch, etc.). The Changeset Controller and Code Host Integration Service are host-agnostic. New hosts added by implementing the interface without modifying core logic.
- **MVP adapters**: GitHub, GitLab (primary). Bitbucket Server/DC, Bitbucket Cloud, Gerrit (secondary).
