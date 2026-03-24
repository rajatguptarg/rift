# rift Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-03-24

## Active Technologies
- Python 3.12 (backend), TypeScript 5.x (frontend) + FastAPI, Pydantic, Motor, python-jose, bcrypt, React 18, React Router 6, TanStack Query, axios (003-restore-auth-access)
- MongoDB for user records and audit events; JWT bearer token held in browser auth state/local storage; existing Redis/Temporal/storage stack unchanged for this feature (003-restore-auth-access)

- Python 3.12 (backend), TypeScript 5.x / React 18 (frontend)
- FastAPI, Motor, python-jose, bcrypt, React Router 6, TanStack Query, axios
- MongoDB for users and roles, browser local storage for the bearer token, existing Redis and object storage unchanged for this feature

## Project Structure

```text
backend/
frontend/
cli/
docs/
specs/
```

## Commands

- `make infra-up`
- `make dev-backend`
- `make dev-frontend`
- `make docker-up-build`
- `make test-backend`
- `make test-frontend`
- `make test`
- `make lint`
- `make format`

## Code Style

- Backend: keep FastAPI code layered as API -> services -> adapters -> models.
- Backend: use Pydantic models for request/response and domain validation.
- Frontend: keep route-level code in `frontend/src/pages`, shared UI in `frontend/src/components`, and API access in `frontend/src/services`.
- Frontend auth work should keep public auth routes outside the protected application shell.

## Recent Changes
- 003-restore-auth-access: Added Python 3.12 (backend), TypeScript 5.x (frontend) + FastAPI, Pydantic, Motor, python-jose, bcrypt, React 18, React Router 6, TanStack Query, axios

- 003-restore-auth-access: planned first-party web authentication, Mongo-backed users, public auth routes, and a bootstrapped local super user

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
