# ADR-010: Auth Implementation — Phase 1 (Infrastructure) and Phase 2 (Core Auth)

**Status**: Accepted
**Date**: 2026-03-24
**Deciders**: Rift Platform Team
**Feature Branch**: `003-restore-auth-access`

---

## Context

ADR-009 established the decision to introduce first-party web authentication with a JWT-based sign-in/sign-up flow and a bootstrap super-user. This ADR records the concrete implementation choices made during Phase 1 (infrastructure scaffolding) and Phase 2 (core auth backend and frontend wiring).

Phase 1 tasks (T001–T003) laid down the structural groundwork: bootstrap settings, test fixtures, and TypeScript type contracts. Phase 2 tasks (T004–T011) delivered the expanded user model, MongoDB user repository, auth service, updated middleware and dependency injection, refactored auth state hook, auth UI components, and fully wired application routing.

---

## Decisions

### User model expansion (T004)

The `User` Pydantic model is extended to carry all fields required for first-party local authentication: `username`, `password_hash`, `role` (`AccessRole` enum), `bootstrap_managed` flag, `last_login_at`, and `updated_at`. A `UserSummary` projection is added as the public-facing shape returned in auth responses so that `password_hash` is never serialised to API consumers.

`AccessRole` is implemented as `StrEnum` (`SUPER_USER`, `STANDARD`). `StrEnum` was chosen over a plain `str` + `Literal` union because it is natively serialisable by Pydantic v2, participates correctly in MongoDB queries, and remains readable in JWT payloads without an extra serialisation step.

### User repository (T005)

`UserRepository` subclasses the existing `BaseRepository[User]` pattern. Case-insensitive username lookup is enforced at the driver level (`username.lower()` before query) rather than via a MongoDB collation index, keeping the repository portable and keeping the index definition simple. A `ensure_unique_username_index` helper is provided so startup code can guarantee the constraint without coupling the repository to application lifecycle hooks.

### Auth service (T006)

`AuthService` encapsulates password hashing (`bcrypt` via `passlib`), JWT issuance (`python-jose`), sign-in, and sign-up. These responsibilities live in a service layer rather than directly in FastAPI route handlers to keep business logic testable without an HTTP layer.

Passwords are hashed with bcrypt (`CryptContext(schemes=["bcrypt"])`). Token payloads include `sub` (user ID), `username`, `role`, `email`, `jti` (UUID hex), `iat`, and `exp`. The `role` claim in the JWT is informational only — the authoritative check on protected endpoints reads `role` from the database via `get_current_user`, not from the token, to prevent privilege escalation through stale tokens.

### Middleware update (T007a)

The `_PUBLIC_PREFIXES` tuple is promoted to a module-level constant and extended with the two auth endpoints (`/api/v1/auth/sign-in`, `/api/v1/auth/sign-up`). The decoded `username` and `role` claims are now stored on `request.state` alongside `user_id` and `email`, making them available to downstream handlers without a database round-trip for display-only use cases.

### Dependency injection update (T007b)

`get_current_user` is upgraded from a lightweight stub that reconstructed a `User` from request state alone to a full database lookup via `UserRepository`. This ensures the user object is authoritative and that deactivated or deleted accounts are rejected at the dependency layer rather than silently succeeding.

A new `require_super_user` guard dependency and `SuperUserDep` alias are introduced to allow individual routes to declare super-user access requirements declaratively.

### Frontend auth hook refactor (T008)

`useAuth` is redesigned so that:

- The context carries a full `UserSummary` object rather than just a token string, enabling avatar, role display, and conditional UI without additional queries.
- On mount, if a stored token exists, the hook calls `GET /api/v1/auth/me` to rehydrate the user object. A failure clears the token (handles expired sessions gracefully).
- The `login` callback now accepts a full `AuthSessionResponse` so the user object is populated immediately after sign-in without a second round-trip.
- `isAuthenticated` is `false` while the rehydration fetch is in-flight (`isLoading: true`), preventing a flash-of-unauthenticated-content redirect to `/login`.

### Auth UI components (T009)

`AuthLayout` and `AuthForm` are introduced as generic, reusable primitives. `AuthLayout` renders the centred card shell with the RIFT wordmark. `AuthForm` is a controlled form driven by a `fields` descriptor array, handling local loading state and error display. This design decouples the form rendering from the auth API calls and allows `LoginPage` and `SignUpPage` to remain declarative.

### Route protection (T011)

`App.tsx` replaces a flat route tree with two nested layout routes:

- `PublicLayout` wraps `/login` and `/signup`. Authenticated users are redirected to their intended destination (or `/batch-changes` as a default).
- `ProtectedLayout` wraps all application routes. Unauthenticated users are redirected to `/login` with the intended path stored in `location.state.returnTo` so the login page can redirect back after a successful sign-in.

A wildcard `*` route and explicit stub routes for `/changesets`, `/templates`, and `/audit` render `NotFound` to prevent blank screens on unimplemented navigation targets.

---

## Alternatives Considered

### Resolve user from JWT claims only (no DB lookup in `get_current_user`)

**Rejected.** Relying solely on the JWT payload means revoked or deleted accounts would continue to authenticate until the token expires. Reading from the database ensures that the `role` and existence of the user are always authoritative.

### Global loading spinner vs. null render during rehydration

`PublicLayout` returns `null` while `isLoading` is true (no render). `ProtectedLayout` renders a centred loading message. This asymmetry is intentional: public pages (login/signup) do not need to show anything while checking auth status, but the app shell would produce a jarring redirect if it unmounted too quickly.

### Separate `UserProfile` model for API responses

The existing `UserResponse` and new `UserSummary` serve slightly different shapes. `UserSummary` is the canonical public-facing projection used in auth responses and the `/me` endpoint. `UserResponse` is retained for admin-facing endpoints that may need additional fields. Consolidating them was considered but deferred to avoid scope creep.

---

## Consequences

### Positive

- All auth round-trips (`sign-in`, `sign-up`, `/me`) are handled end-to-end with well-typed request/response contracts shared between backend and frontend.
- Protected routes are enforced uniformly at the React Router level with no per-page guard repetition.
- The `SuperUserDep` alias makes it trivial to add super-user-only routes.
- Bootstrap credentials are configuration-only and not hard-coded in source.

### Negative / Trade-offs

- `get_current_user` now issues a MongoDB query on every authenticated request. A caching layer (Redis or in-process short-lived cache keyed on `user_id`) may be needed at higher traffic volumes.
- `passlib` with `bcrypt` adds a C-extension dependency; ensure the Docker image includes the required build tools or pin to a pre-built wheel.

### Neutral

- Password reset, email verification, and MFA are explicitly out of scope for this phase.
- The `bootstrap_managed` flag on `User` is set by startup logic (not yet implemented in this phase); the model and repository support it, but the seeding code will be delivered in a subsequent phase.

---

## References

- [ADR-009: Local Auth Bootstrap Decision](adr-009-local-auth-bootstrap.md)
- [Spec 003: Restore Authenticated Access](../../specs/003-restore-auth-access/spec.md)
- `backend/src/models/user.py`
- `backend/src/adapters/mongo/user_repo.py`
- `backend/src/services/auth_service.py`
- `backend/src/api/middleware/auth.py`
- `backend/src/api/dependencies.py`
- `frontend/src/hooks/useAuth.tsx`
- `frontend/src/components/auth/AuthLayout.tsx`
- `frontend/src/components/auth/AuthForm.tsx`
- `frontend/src/pages/Auth/LoginPage.tsx`
- `frontend/src/pages/Auth/SignUpPage.tsx`
- `frontend/src/App.tsx`
