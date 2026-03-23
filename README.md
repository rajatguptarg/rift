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
│  JWT middleware · AES-256-GCM encryption                 │
└──────┬───────────────────────────┬───────────────────────┘
       │ Motor (async)             │ Temporal SDK
┌──────▼──────┐         ┌──────────▼──────────────────────┐
│  MongoDB 7  │         │  Temporal Worker (Python)        │
│  (primary   │         │  PreviewWorkflow · ApplyWorkflow │
│   store)    │         │  activities: clone · exec · diff │
└─────────────┘         └─────────────────────────────────┘
       │ redis.asyncio
┌──────▼──────┐
│  Redis 7.2  │  (cache / pub-sub future)
└─────────────┘
```

**Layers:**

- `backend/src/core/` — settings, logging, error types, encryption
- `backend/src/adapters/` — MongoDB repos, Redis client, S3, code-host adapters (GitHub/GitLab)
- `backend/src/models/` — Pydantic v2 domain models with state machines
- `backend/src/services/` — business logic (batch change CRUD, execution orchestration, reconciliation, analytics)
- `backend/src/workflows/` — Temporal workflows and activities
- `backend/src/api/` — FastAPI routes, middleware, DI
- `frontend/src/` — React 18 + TypeScript SPA (TanStack Query, React Router, Tailwind CSS)
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
| SeaweedFS S3 API | http://localhost:9000 (minioadmin / minioadmin) |
| SeaweedFS Filer UI | http://localhost:8888 |

> The frontend nginx container proxies `/api/*` → the `api` container automatically, so there are no CORS issues and no `.env` file is needed for Docker mode.

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
# Starts MongoDB, Redis, Temporal, SeaweedFS in Docker (detached)
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
# Vite dev server with hot-reload at http://localhost:3000
```

Or start everything in one go (requires separate terminal tabs per process):

```bash
make dev   # infra-up + dev-backend + dev-frontend (via concurrently)
```

---

## Running Tests

**Backend:**

```bash
make test-backend
# pytest with --cov-fail-under=80
```

**Frontend:**

```bash
make test-frontend
# vitest with coverage
```

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

All configuration is read from environment variables (see `.env.example`):

| Variable | Required | Description |
|---|---|---|
| `MONGODB_URL` | ✓ | MongoDB connection string |
| `REDIS_URL` | ✓ | Redis connection string |
| `JWT_SECRET` | ✓ | Secret for JWT verification |
| `APP_SECRET_KEY` | ✓ | AES key derivation seed (local dev) |
| `TEMPORAL_HOST` | ✓ | Temporal frontend address |
| `S3_BUCKET` | | Object store bucket for logs/patches |
| `AWS_REGION` | | AWS region for S3 |
| `LOG_LEVEL` | | `DEBUG` / `INFO` / `WARNING` (default: `INFO`) |

---

## Contributing

1. Fork the repository and create a branch: `feat/XYZ-123-short-description`
2. Make your changes following the layer conventions above
3. Add or update tests (backend: pytest, frontend: vitest + Playwright)
4. Ensure `make lint` and `make test` pass
5. Commit using [Conventional Commits](https://www.conventionalcommits.org/) with a Jira ticket: `feat(api): add template generation [RIFT-42]`
6. Open a pull request against `main` with the PR template

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

---

## License

[MIT](LICENSE)
