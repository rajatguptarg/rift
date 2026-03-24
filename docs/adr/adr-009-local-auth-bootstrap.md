# ADR-009: Add Local Authentication Bootstrap with a Default Super User

**Status**: Accepted  
**Date**: 2026-03-24  
**Deciders**: Rift Platform Team  
**Feature Branch**: `003-restore-auth-access`

---

## Context

The Rift web application already assumes authenticated access. Frontend behavior redirects signed-out users to a login destination, and backend APIs reject requests without valid credentials.

At the moment, there is no usable web sign-in or sign-up experience. As a result, users who open the application are redirected away from product pages and encounter a blank screen instead of a recoverable authentication path. This blocks all web usage, including the batch-change creation flow.

The product also needs a guaranteed way to recover administration in a brand-new local environment. Without a known initial administrative account, a fresh instance can become unusable before any roles or users exist.

---

## Decision

Introduce a first-party web authentication flow that supports both sign-in and sign-up for Rift users, using JWT bearer tokens so the SPA remains compatible with the existing API authorization pattern.

Bootstrap a default super user role and seed a default local administrative account with username `master` and password `master` so a clean local environment always has one known-good administrative login.

Source the bootstrap credentials from runtime environment variables documented for local development, rather than hard-coding them in application logic.

Treat self-service sign-up accounts as standard users by default. Elevated privileges remain reserved for the bootstrapped super user unless a later administrative action changes a user's role.

Render authentication on explicit public routes and reserve the full application shell for authenticated routes so missing or expired sessions do not produce blank pages.

---

## Alternatives Considered

### Keep token-only access and require manual database seeding

**Rejected.** This leaves the product unusable from the web UI and makes first-run access dependent on out-of-band operational steps.

### Require external identity integration first

**Rejected.** SSO or directory-backed authentication may be desirable later, but it adds integration scope and does not solve immediate local usability or first-run recovery.

### Provide sign-in only and skip self-service sign-up

**Rejected.** The requested feature explicitly includes both sign-in and sign-up, and sign-up reduces operator involvement for first-time access in local environments.

### Create the super user manually after startup

**Rejected.** Manual creation weakens the guarantee that a fresh local instance is always recoverable by the operator.

---

## Consequences

### Positive

- Rift gains a recoverable first-run access path for the web product.
- A fresh local instance always has one working administrative login.
- The application can redirect signed-out users to a real authentication experience instead of a blank page.
- The new auth flow fits the existing bearer-token middleware and frontend API client instead of requiring a session-transport rewrite.

### Negative / Trade-offs

- Shipping known default credentials increases operational risk if they are not rotated or replaced promptly after first use.
- The platform now needs a minimal role model from the start, even before broader RBAC work is complete.

### Neutral

- This decision restores web access for the product but does not address advanced identity features such as password recovery, MFA, or external SSO.
- CLI authentication remains unchanged by this decision.

---

## Implementation Notes

Implemented in feature branch `003-restore-auth-access` (2026-03-24):

- **`backend/src/models/user.py`** — `User` expanded with `username`, `password_hash`, `role` (AccessRole enum), `bootstrap_managed`, `last_login_at`
- **`backend/src/adapters/mongo/user_repo.py`** — `UserRepository` with `find_by_username`, `find_bootstrap_user`, `update_last_login`, `ensure_unique_username_index`
- **`backend/src/services/auth_service.py`** — `AuthService.sign_in`, `AuthService.sign_up`, `hash_password`, `verify_password`, JWT issuance
- **`backend/src/services/bootstrap_service.py`** — `BootstrapService.seed()` — idempotent startup seeding from env vars
- **`backend/src/api/routes/auth.py`** — `POST /api/v1/auth/sign-in`, `POST /api/v1/auth/sign-up`, `GET /api/v1/auth/me`
- **`backend/src/api/middleware/auth.py`** — Public path exemptions include `/api/v1/auth/sign-in` and `/api/v1/auth/sign-up`
- **`backend/src/api/dependencies.py`** — `get_current_user` performs real DB lookup; `SuperUserDep` added
- **`frontend/src/hooks/useAuth.tsx`** — Carries `UserSummary`, handles `isLoading`, rehydrates from `/api/v1/auth/me` on mount
- **`frontend/src/App.tsx`** — `PublicLayout` / `ProtectedLayout` route split; wildcard routes to `NotFound`
- **`frontend/src/pages/Auth/LoginPage.tsx`** and **`SignUpPage.tsx`** — Auth UI screens
- **`frontend/src/components/auth/AuthLayout.tsx`** and **`AuthForm.tsx`** — Reusable auth UI primitives
- **`frontend/src/components/layout/SideNav.tsx`** — Sign-out button and Super User badge

## References

- [Authentication access specification](../../specs/003-restore-auth-access/spec.md)
- [Implementation plan](../../specs/003-restore-auth-access/plan.md)
- [Quickstart guide](../../specs/003-restore-auth-access/quickstart.md)
- [frontend/src/hooks/useAuth.tsx](../../frontend/src/hooks/useAuth.tsx)
- [frontend/src/services/api.ts](../../frontend/src/services/api.ts)
- [backend/src/api/middleware/auth.py](../../backend/src/api/middleware/auth.py)
- [backend/src/api/routes/auth.py](../../backend/src/api/routes/auth.py)
- [backend/src/services/bootstrap_service.py](../../backend/src/services/bootstrap_service.py)
- [README](../../README.md)
