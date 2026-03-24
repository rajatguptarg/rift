# Rift — Batch Changes Platform

Rift is an open-source platform for orchestrating large-scale, automated code changes across many repositories simultaneously. Define a batch spec in YAML, preview the diffs, and publish pull requests to GitHub or GitLab — all from a single UI or CLI.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Option A: Full Docker Stack (recommended)](#option-a-full-docker-stack-recommended)
  - [Option B: Local Development (hot-reload)](#option-b-local-development-hot-reload)
- [Running Tests](#running-tests)
- [CLI Usage](#cli-usage)
- [Configuration](#configuration)
- [Specifications](#specifications)
- [Contributing](#contributing)
- [ADRs](#adrs)

---

## Overview

Rift is a self-hosted alternative to Sourcegraph Batch Changes, designed for teams that need:

- **Bulk automation**: Run the same transformation across hundreds of repositories
- **Full audit trail**: Every action is logged, every diff is stored
- **Credential isolation**: Per-namespace encrypted tokens, not a single shared bot
- **Template library**: Reusable batch spec templates with dynamic form fields

---

## Features

| Feature | Description |
|---|---|
| Batch spec YAML editor | In-browser IDE panel with syntax highlighting |
| Fan-out execution | Temporal-powered parallel workspace execution per repo |
| Real-time progress | Server-Sent Events stream for live execution view |
| Changeset management | Track PR state (open, merged, closed) with burndown analytics |
| CLI | `rift login`, `rift batch preview`, `rift batch apply` |
| Credential store | AES-256-GCM encrypted tokens per namespace/org/user |
| Template library | Parameterized batch spec templates with validation |
| Audit log | Immutable audit events for every state transition |

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend (React)                     │
│  BatchChangesList → BatchSpecEditor → ExecutionView      │
│  ChangesetDashboard → CredentialSettings                 │
└──────────────────────┬──────────────────────────────────┘
                       │ REST + SSE
┌──────────────────────▼──────────────────────────────────┐
│                  API (FastAPI / Python)                  │
│  routes/ → services/ → adapters/                        │
│  JWT middleware · SHA-256 prehashed bcrypt passwords     │
│  AES-256-GCM encryption                                  │
└──────┬───────────────────────────┬───────────────────────┘
       │ Motor (async)             │ Temporal SDK / boto3 S3
┌──────▼──────┐         ┌──────────▼──────────────────────┐
│  MongoDB 7  │         │  Temporal Worker (Python)        │
│  (primary   │         │  PreviewWorkflow · ApplyWorkflow │
│   store)    │         │  activities: clone · exec · diff │
└─────────────┘         └──────────┬──────────────────────┘
       │ redis.asyncio             │
┌──────▼──────┐          ┌─────────▼─────────┐
│  Redis 7.2  │          │  SeaweedFS S3     │
│  (cache /   │          │  logs · patches   │
│   pub/sub)  │          │  presigned URLs   │
└─────────────┘          └───────────────────┘
```

**Layers:**

- `backend/src/core/` — settings, logging, error types, encryption
- `backend/src/adapters/` — MongoDB repos, Redis client, SeaweedFS/S3 object store, code-host adapters (GitHub/GitLab)
- `backend/src/models/` — Pydantic v2 domain models with state machines
- `backend/src/services/` — business logic (batch change CRUD, execution orchestration, reconciliation, analytics)
- `backend/src/workflows/` — Temporal workflows and activities
- `backend/src/api/` — FastAPI routes, middleware, DI
- `frontend/src/` — React 18 + TypeScript SPA (TanStack Query, React Router, Tailwind CSS)
- `frontend/tests/` — Vitest unit/integration coverage suites and Playwright end-to-end flows
- `cli/src/` — TypeScript CLI (commander)

Design tokens and component patterns follow the **Kinetic Monolith** design system (see [ADR-006](docs/adr/adr-006-design-system-kinetic-monolith.md)).

---

## Getting Started

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) ≥ 4.x (required for both options)
- Python 3.12 _(Option B only)_
- Node.js 20 LTS _(Option B only)_
- `make`

---

### Option A: Full Docker Stack (recommended)

Runs every service — MongoDB, Redis, Temporal, SeaweedFS, API, Temporal worker, and the React frontend — in Docker. No local language runtimes required.

**1. Clone and start**

```bash
git clone https://github.com/your-org/rift.git
cd rift
make docker-up-build      # builds images and starts all services (first run)
```

On subsequent runs:

```bash
make docker-up            # start (no rebuild)
make docker-down          # stop and remove containers + volumes
make docker-logs          # tail api / worker / frontend logs
```

**2. Open the app**

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| API / OpenAPI docs | http://localhost:8000/docs |
| Temporal UI | http://localhost:8088 |
| SeaweedFS S3 API | http://localhost:9000 |
| SeaweedFS Filer UI | http://localhost:8888 |

> The frontend nginx container proxies `/api/*` → the `api` container automatically, so there are no CORS issues and no `.env` file is needed for Docker mode.
> Default local object-store credentials are defined in [`.env.example`](.env.example).
> Frontend Docker builds intentionally ignore local `*.tsbuildinfo` files and install explicit Node typings from `frontend/package.json` so `make docker-up-build` stays reproducible across machines.

---

### Option B: Local Development (hot-reload)

Run infrastructure in Docker but the application services locally for faster iteration.

**1. Clone and configure**

```bash
git clone https://github.com/your-org/rift.git
cd rift
cp .env.example .env
# Review .env — defaults work for local Docker infra as-is
```

**2. Start infrastructure only**

```bash
make infra-up
# Starts MongoDB, Redis, Temporal (with its local Postgres backing DB), Temporal UI,
# SeaweedFS, and bucket init in Docker
```

**3. Start the API**

```bash
cd backend && pip install -e ".[dev]" && cd ..
make dev-backend
# FastAPI with hot-reload at http://localhost:8000
# OpenAPI docs at http://localhost:8000/docs
```

**4. Start the Temporal worker**

```bash
make dev-worker
# Worker connects to localhost:7233
```

**5. Start the frontend**

```bash
cd frontend && npm install && cd ..
make dev-frontend
# Vite dev server with hot-reload at http://localhost:5173
```

The frontend build compiles `vite.config.ts` via `tsconfig.node.json`, so keep dev dependencies installed before running `npm run build` or `make dev-frontend`.

Run `make dev-backend`, `make dev-worker`, and `make dev-frontend` in separate terminals for local development.

---

## Running Tests

**Backend:**

```bash
make test-backend
# pytest with --cov-fail-under=5
```

**Frontend:**

```bash
make test-frontend
# vitest with coverage

# Interactive Vitest UI (browser-based test runner)
cd frontend && npm run test:ui

# Browser end-to-end auth flows
cd frontend && npm run test:e2e
```

Vitest runs the unit and integration suites and explicitly excludes `frontend/tests/e2e/**` so Playwright specs are only executed via `npm run test:e2e`. The shared frontend test setup also installs an in-memory `localStorage` mock to keep auth tests stable across local Node runtimes and CI.

**All:**

```bash
make test
```

**Linting:**

```bash
make lint          # ruff (backend) + eslint (frontend)
make format        # ruff format + prettier
```

---

## CLI Usage

```bash
# Install CLI
cd cli && npm install && npm run build
npm link   # or: node dist/index.js

# Login
rift login --url http://localhost:8000 --token <your-jwt>

# Preview a batch spec
rift batch preview --spec path/to/spec.yaml --namespace my-org

# Apply a batch change
rift batch apply --id <batch-change-id>
```

---

## Configuration

All configuration is read from environment variables (see [`.env.example`](.env.example)). Docker mode injects these through Compose; hot-reload mode reads them from `.env`.

| Variable | Required | Description |
|---|---|---|
| `MONGODB_URL` | ✓ | MongoDB connection string |
| `MONGODB_DATABASE` | ✓ | MongoDB database name |
| `REDIS_URL` | ✓ | Redis connection string |
| `JWT_SECRET` | ✓ | Secret for JWT verification |
| `JWT_ALGORITHM` | | JWT signing algorithm (default: `HS256`) |
| `JWT_EXPIRE_MINUTES` | | Access token lifetime in minutes (default: `1440`) |
| `APP_SECRET_KEY` | ✓ | AES key derivation seed (local dev) |
| `TEMPORAL_HOST` | ✓ | Temporal frontend address |
| `TEMPORAL_NAMESPACE` | ✓ | Temporal namespace |
| `TEMPORAL_TASK_QUEUE` | ✓ | Temporal task queue used by the worker |
| `OBJECT_STORE_ENDPOINT` | ✓ | SeaweedFS S3 endpoint |
| `OBJECT_STORE_BUCKET` | ✓ | Object store bucket for logs/patches |
| `OBJECT_STORE_ACCESS_KEY` | ✓ | S3 access key for local object storage |
| `OBJECT_STORE_SECRET_KEY` | ✓ | S3 secret key for local object storage |
| `OBJECT_STORE_REGION` | ✓ | AWS region passed to boto3 |
| `BOOTSTRAP_SUPERUSER_USERNAME` | | Bootstrap super-user username (default: `master`) — change in production |
| `BOOTSTRAP_SUPERUSER_PASSWORD` | | Bootstrap super-user password (default: `master`) — change in production; long secrets are supported |
| `BOOTSTRAP_SUPERUSER_DISPLAY_NAME` | | Bootstrap super-user display name (default: `Rift Master`) |
| `API_CORS_ORIGINS` | | Allowed browser origins for local frontend development as a JSON array |
| `LOG_LEVEL` | | `DEBUG` / `INFO` / `WARNING` (default: `INFO`) |

Password storage now uses a SHA-256 prehash before bcrypt, which keeps bootstrap and user passwords compatible with modern `bcrypt` releases and avoids the 72-byte input limit. Existing legacy `$2...` bcrypt hashes are still accepted on sign-in.

---

## Specifications

Product and delivery specifications live in [`specs/`](specs/):

| Spec | Title | Status |
|---|---|---|
| [001](specs/001-batch-changes-platform/spec.md) | Batch Changes Platform | Accepted |
| [002](specs/002-replace-minio-storage/spec.md) | Replace MinIO with Open-Source S3-Compatible Storage | Accepted |
| [003](specs/003-restore-auth-access/spec.md) | Restore Authenticated Access with Sign-In, Sign-Up, and Super User Bootstrap | Planning complete |

Each spec may also include supporting artifacts such as checklists, contracts, research notes, plans, quickstarts, data models, and tasks.

Spec `003-restore-auth-access` now includes its Phase 0 and Phase 1 planning artifacts in [`specs/003-restore-auth-access/`](specs/003-restore-auth-access/), including `research.md`, `data-model.md`, `quickstart.md`, and the auth/routing contracts.

---

## Contributing

1. Fork the repository and create a branch: `feat/XYZ-123-short-description`
2. Make your changes following the layer conventions above
3. Add or update tests (backend: pytest, frontend: Vitest for unit/integration and Playwright for `frontend/tests/e2e`)
4. Ensure `make lint` and `make test` pass, and run `cd frontend && npm run test:e2e` when browser flows are affected
5. Commit using [Conventional Commits](https://www.conventionalcommits.org/) with a Jira ticket: `feat(api): add template generation [RIFT-42]`
6. Open a pull request against `main` with the required PR sections: what changed, why it is needed, how it was tested, and the checklist from the repo guidelines

See [CLAUDE.md](CLAUDE.md) for full commit message and PR guidelines.

---

## ADRs

Architectural decisions are recorded in [`docs/adr/`](docs/adr/):

| ADR | Title |
|---|---|
| [001](docs/adr/adr-001-mongodb-primary-store.md) | MongoDB as Primary Data Store |
| [002](docs/adr/adr-002-temporal-orchestration.md) | Temporal for Workflow Orchestration |
| [003](docs/adr/adr-003-rest-sse-api-style.md) | REST + Server-Sent Events API Style |
| [006](docs/adr/adr-006-design-system-kinetic-monolith.md) | Kinetic Monolith Design System |
| [007](docs/adr/adr-007-seaweedfs-storage.md) | SeaweedFS for Local Object Storage |
| [008](docs/adr/adr-008-explicit-frontend-node-types.md) | Explicit Node Typings for Frontend Builds |
| [009](docs/adr/adr-009-local-auth-bootstrap.md) | Local Authentication Bootstrap with a Default Super User |
| [010](docs/adr/adr-010-auth-implementation-phase1-phase2.md) | Auth Implementation — Phase 1 (Infrastructure) and Phase 2 (Core Auth) |
| [011](docs/adr/adr-011-auth-implementation-phase3.md) | Auth Implementation — Phase 3 (Routes, Bootstrap Service, and Frontend Integration) |
| [012](docs/adr/adr-012-password-hash-compatibility.md) | Password Hash Compatibility and Long-Secret Support |
| [013](docs/adr/adr-013-frontend-test-runner-boundaries.md) | Frontend Test Runner Boundaries |

---

## License

[MIT](LICENSE)
