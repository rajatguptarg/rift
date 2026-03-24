# ADR-011: Auth Implementation — Phase 3 (Routes, Bootstrap Service, and Frontend Integration)

**Date:** 2026-03-24
**Status:** Accepted
**Deciders:** Rift core team

---

## Context

Phase 1 established the auth infrastructure (JWT middleware, password hashing, user model, `UserRepository`).
Phase 2 delivered the core auth services (`AuthService`, `get_current_user` dependency, `UserRepository` with `find_by_id`).

Phase 3 completes the end-to-end auth story by wiring the API surface, seeding the bootstrap super user on startup, and integrating auth state cleanly into the React frontend.

---

## Decision

### T018 + T029: Auth API routes (`POST /auth/sign-in`, `POST /auth/sign-up`, `GET /auth/me`)

A dedicated `auth.py` router is created at `backend/src/api/routes/auth.py` under the `/api/v1/auth` prefix.

- `POST /auth/sign-in` delegates to `AuthService.sign_in`, records a `LOGIN` audit event on success, and returns `AuthSessionResponse` (token + user summary).
- `POST /auth/sign-up` delegates to `AuthService.sign_up` with a 201 response; username conflicts map to HTTP 409 with a `USERNAME_CONFLICT` error code.
- `GET /auth/me` uses `CurrentUserDep` to return the hydrated user from the database, confirming the token is still valid.

Pydantic request models `SignInRequest` and `SignUpRequest` enforce field-level constraints (min/max length, username pattern) so validation errors are surfaced before hitting the service layer.

### T023: Audit event on sign-in

The `AuditService.record(action=AuditAction.LOGIN)` call is placed inside the sign-in route handler (not the service), keeping the service layer free of cross-cutting concerns. The actor, resource type, and resource ID are all set to the signing-in user.

### T019 + T037: Register auth router and invoke bootstrap in `main.py`

The auth router is registered before the remaining routers so `/api/v1/auth/*` routes appear first in the OpenAPI schema. The startup lifecycle hook now calls `BootstrapService(db).seed()` after MongoDB and Redis connect, ensuring the super user exists before the first request is served.

### T036: `BootstrapService`

A dedicated service class (`bootstrap_service.py`) handles super-user seeding:

- Calls `ensure_unique_username_index()` on every startup (idempotent index creation).
- Checks for an existing bootstrap-managed user with `find_bootstrap_user()`.
- If absent, creates a `SUPER_USER` from environment config (`BOOTSTRAP_SUPERUSER_*` vars).
- Logs the outcome at `INFO` level via structlog.

Separating this concern into its own service makes it testable in isolation from both the startup lifecycle and `AuthService`.

### T021: 401 recovery via custom DOM event

The Axios response interceptor in `api.ts` previously used `window.location.href` for 401 redirects. This hard navigation bypasses React Router's history and breaks the return-to-URL pattern.

The interceptor now dispatches a `CustomEvent("rift:auth:expired")` and `AuthProvider` listens for this event in a `useEffect`, clearing auth state without forcing a full page reload. The React Router `<Navigate>` in the route guard then redirects cleanly within the SPA history.

### T039: SideNav — sign-out button and super-user badge

`SideNav.tsx` is updated to:

- Import `useAuth` and call `logout()` + `navigate("/login", { replace: true })` on sign-out.
- Display the authenticated user's `display_name` in the bottom panel.
- Show a "Super User" badge when `user.role === "SUPER_USER"`.

This keeps the admin identity visually distinct without separate routes or layout forks.

---

## Alternatives Considered

### Alt A: Sign-in route calls `AuditService` inside `AuthService`

Injecting `AuditService` into `AuthService` would create a dependency between two peer services. Keeping the audit call in the route handler follows the principle that side effects belong at the HTTP boundary layer.

### Alt B: Bootstrap in a CLI command instead of startup hook

A CLI seed command gives operators explicit control but adds friction for local development and increases the chance of a missing super user. The startup hook approach is self-healing and matches the zero-config ethos established by ADR-009.

### Alt C: Hard navigation on 401 (`window.location.href = "/login"`)

Already existed. Replaced because it breaks React Router state, loses the `from` location for return-to-route, and forces full page re-initialisation on every token expiry.

---

## Consequences

**Positive:**
- Full auth API is available: sign-in, sign-up, and current-user introspection.
- Bootstrap super user is idempotently created on every startup.
- 401 recovery is clean and router-compatible.
- Sign-out is accessible from the navigation without a separate settings page.
- All new logic is covered by unit, integration, and functional tests.

**Negative / Trade-offs:**
- `main.py` startup now performs a DB query (bootstrap seed check). In high-availability deployments with multiple API instances, this creates a harmless race on first boot; the unique index ensures only one user is created.
- The `rift:auth:expired` event is a non-standard browser API pattern. Teams unfamiliar with custom events may find it unexpected; the pattern is documented in this ADR and in the `api.ts` inline comment.

---

## Related

- [ADR-009](adr-009-local-auth-bootstrap.md) — Decision to use a default super user for local bootstrap
- [ADR-010](adr-010-auth-implementation-phase1-phase2.md) — Phase 1 and Phase 2 auth infrastructure
- [Spec 003](../../specs/003-restore-auth-access/spec.md) — Full auth restoration specification
