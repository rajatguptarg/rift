# Quickstart: Verify Local Authentication Access

**Feature**: `003-restore-auth-access`  
**Audience**: Developers validating the local auth-access flow after implementation  
**Date**: 2026-03-24

---

## What This Feature Adds

- A usable Rift sign-in screen for signed-out users
- Self-service sign-up for standard users
- A bootstrapped local super user with username `master` and password `master`
- Explicit route handling so auth failures and unsupported routes do not produce blank pages

---

## Environment Setup

Add these local-development auth values to `.env`:

```env
BOOTSTRAP_SUPERUSER_USERNAME=master
BOOTSTRAP_SUPERUSER_PASSWORD=master
BOOTSTRAP_SUPERUSER_DISPLAY_NAME=Rift Master
```

Mirror the same values in `docker-compose.yml` for Docker-based local startup.

> These values are for local development only. Runtime code must read them from environment variables rather than hard-coding them.

---

## Start the Stack

### Option A: Docker stack

```bash
make docker-up-build
```

Open:

- Frontend: `http://localhost:3000`
- API docs: `http://localhost:8000/docs`

### Option B: Local hot reload

```bash
cp .env.example .env
make infra-up
make dev-backend
make dev-worker
make dev-frontend
```

Open the frontend at `http://localhost:5173`.

---

## Manual Verification Flow

### 1. Sign in with the bootstrap super user

1. Open the frontend in a clean browser session.
2. Confirm the application shows a login screen instead of a blank page.
3. Sign in with:
   - Username: `master`
   - Password: `master`
4. Confirm you land on `/batch-changes` (or your originally requested protected route).

### 2. Create a standard user account

1. Sign out.
2. Open the sign-up flow.
3. Register a new user with a unique username and password.
4. Confirm the new user is signed in and can reach the main Rift UI without blank content.

### 3. Verify expired-session behavior

1. Sign in.
2. In browser devtools, delete or corrupt the stored auth token.
3. Navigate to a protected route such as `/batch-changes/new`.
4. Confirm the app sends you to `/login` and renders a usable auth screen instead of an empty shell.

### 4. Verify unsupported-route rendering

1. While signed in, open `/changesets`, `/templates`, and `/audit`.
2. Confirm each path renders an explicit fallback page instead of blank content.
3. Open `/batch-changes/<existing-id>` and confirm it resolves to `/batch-changes/<id>/spec`.

---

## Automated Test Commands

### Backend

```bash
make test-backend
```

### Frontend

```bash
make test-frontend
```

### Functional browser flows

```bash
cd frontend
npm run test:e2e
```

---

## Expected Test Coverage by Layer

- **Unit**: password hashing, token issuance/parsing, auth hook state transitions, protected-route logic
- **Integration**: Mongo-backed sign-up/sign-in/current-user API behavior, frontend auth-form submission and error states
- **Functional**: login, sign-up, sign-out, expired-session redirect, unsupported-route fallback rendering
