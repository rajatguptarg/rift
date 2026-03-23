# Quickstart: Rift Batch Changes Platform

**Date**: 2026-03-23

This guide gets you from zero to a running local development environment.

## Prerequisites

- Python 3.12+
- Node.js 20+ and npm 10+
- Docker (for testcontainers, MongoDB, Redis)
- Docker Compose (for infrastructure services)
- Git

## 1. Clone and Branch

```bash
git clone <repository-url>
cd rift
git checkout 001-batch-changes-platform
```

## 2. Environment Setup

Copy the example environment file and fill in local values:

```bash
cp .env.example .env
```

Edit `.env` with your local values. The `.env.example` file documents every required variable with placeholder values.

## 3. Start Infrastructure Services

```bash
docker compose up -d mongodb redis temporal
```

This starts:
- **MongoDB** on `localhost:27017`
- **Redis** on `localhost:6379`
- **Temporal** dev server on `localhost:7233` (UI on `localhost:8233`)

## 4. Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Run the backend API server:

```bash
uvicorn src.main:app --reload --port 8000
```

The API is available at `http://localhost:8000`. OpenAPI docs at `http://localhost:8000/docs`.

Start the Temporal worker (separate terminal):

```bash
source .venv/bin/activate
python -m src.workflows.worker
```

## 5. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend dev server runs at `http://localhost:5173` with HMR.

## 6. CLI Setup

```bash
cd cli
npm install
npm run build
npm link
```

Authenticate:

```bash
rift login http://localhost:8000
```

## 7. Running Tests

### Backend

```bash
cd backend
source .venv/bin/activate

# Unit tests only (fast, no Docker needed)
pytest tests/unit/ -v

# Integration tests (requires Docker for testcontainers)
pytest tests/integration/ -v

# All tests with coverage report
pytest --cov=src --cov-report=term-missing --cov-fail-under=80
```

### Frontend

```bash
cd frontend

# Unit + integration tests
npm test

# Coverage report
npm run test:coverage

# End-to-end tests (requires backend + frontend running)
npx playwright test
```

### CLI

```bash
cd cli
npm test
```

## 8. Verify the Setup

1. Open `http://localhost:5173` — you should see the Batch Changes landing page.
2. Navigate to `/batch-changes` and click "Create batch change".
3. Alternatively, run `rift batch preview -f examples/hello-world.yaml` from the CLI.

## 9. Common Commands

| Task | Command |
|------|---------|
| Backend lint | `cd backend && ruff check src/` |
| Backend format | `cd backend && ruff format src/` |
| Frontend lint | `cd frontend && npm run lint` |
| Frontend format | `cd frontend && npm run format` |
| Helm lint | `helm lint helm/` |
| Full test suite | `make test` (from repo root) |

## Troubleshooting

- **MongoDB connection refused**: Ensure Docker is running and `docker compose up -d mongodb` succeeded.
- **Temporal worker not connecting**: Verify Temporal dev server is up at `localhost:7233`.
- **80% coverage gate failing**: Run `pytest --cov=src --cov-report=html` and open `htmlcov/index.html` to identify uncovered code.
