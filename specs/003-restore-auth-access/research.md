# Research: Restore Authenticated Access with Sign-In, Sign-Up, and Super User Bootstrap

**Feature**: `003-restore-auth-access`  
**Phase**: 0 — Pre-design research  
**Date**: 2026-03-24

## Questions Resolved

| # | Question | Status |
|---|----------|--------|
| Q1 | Which authentication transport best fits the existing Rift stack? | ✅ Resolved |
| Q2 | How should user identity data change to support username/password auth? | ✅ Resolved |
| Q3 | How should the super user role be represented and enforced? | ✅ Resolved |
| Q4 | How should the default `master` account be provisioned without violating secret-management rules? | ✅ Resolved |
| Q5 | How should the frontend eliminate blank pages caused by auth redirects and undeclared routes? | ✅ Resolved |
| Q6 | What planning artifacts and test layers are required for a constitution-compliant implementation? | ✅ Resolved |

---

## Q1: Authentication Transport

### Decision

Use first-party username/password authentication that issues **JWT bearer tokens** through new backend auth endpoints. The frontend keeps using the existing bearer-token pattern by storing the token in auth state/local storage and sending it through the existing axios interceptor.

### Rationale

- The backend already depends on `python-jose` for JWT verification, and the runtime can use `bcrypt` directly for password hashing without changing the existing auth transport.
- The frontend already injects `Authorization: Bearer <token>` headers and clears the token on `401`, so preserving this transport avoids a full auth rewrite.
- CLI auth remains untouched because the feature scope is explicitly the Rift web application.

### Alternatives Considered

- **HttpOnly cookie sessions**: Rejected for this feature because it would require changing the existing frontend auth transport and middleware contract.
- **Server-stored sessions in Redis or MongoDB**: Rejected as unnecessary complexity for a stateless JWT flow already assumed by the codebase.
- **External SSO / OAuth**: Rejected as out of scope for restoring local web access quickly.

---

## Q2: Identity Model and Sign-Up Shape

### Decision

Extend the user model to support first-party auth with these core fields:

- `username` (unique, primary sign-in identifier)
- `display_name`
- `email` (optional)
- `password_hash`
- `role`
- `bootstrap_managed`
- `last_login_at`
- existing timestamps

Keep `auth_subject`, but derive it from local auth as `local:{username}` rather than an external identity provider subject.

### Rationale

- The spec explicitly requires username/password sign-in and a bootstrap user named `master`.
- The current `User` model has no username or password storage, so it cannot satisfy the requested web auth flow as-is.
- Making email optional reduces friction for the requested local sign-up flow while preserving room for future profile or notification features.
- Prehashing passwords with SHA-256 before bcrypt avoids bcrypt's 72-byte input limit, which matters for operator-supplied bootstrap secrets.

### Alternatives Considered

- **Email-only login**: Rejected because the feature requirement and bootstrap account are username-based.
- **Separate credential document for passwords**: Rejected because the feature only needs a single local auth method and would add unnecessary data-model complexity.
- **Dropping `auth_subject` entirely**: Rejected because existing code and docs already assume the field exists; deriving it locally keeps compatibility.

---

## Q3: Role Representation and Authorization

### Decision

Represent authorization with a simple **role enum on the user record** for this feature, with at least:

- `SUPER_USER`
- `STANDARD`

Include the user role in JWT claims and expose role-aware helpers through API dependencies. Treat self-service sign-up accounts as `STANDARD` by default, and bootstrap the `master` account as `SUPER_USER`.

### Rationale

- The feature only requires a single privileged role and a default non-privileged role.
- Existing backend authorization is thin and currently based on decoded token claims; a single role field fits that model without introducing a broader RBAC system prematurely.
- A role enum on the user record is enough to gate privileged admin actions while keeping future namespace RBAC work open.

### Alternatives Considered

- **Dedicated `roles` collection**: Rejected as too heavy for the requested scope.
- **Per-namespace RBAC implemented now**: Rejected because the feature only needs global bootstrap administration and standard self-service access.
- **Scopes-only tokens without persistent role data**: Rejected because sign-up/bootstrap flows need a durable source of truth for authorization.

---

## Q4: Bootstrap Super User Provisioning

### Decision

Provision the bootstrap super user during API startup with an **idempotent create-if-missing check**, sourcing values from new environment variables:

- `BOOTSTRAP_SUPERUSER_USERNAME`
- `BOOTSTRAP_SUPERUSER_PASSWORD`
- optional `BOOTSTRAP_SUPERUSER_DISPLAY_NAME`

Local development defaults should be documented and wired through `.env.example` and `docker-compose.yml` as `master` / `master`.

### Rationale

- The spec requires a guaranteed first-run admin login.
- The constitution requires secrets and credentials to come from environment variables at runtime rather than checked-in runtime constants.
- Startup bootstrap ensures a clean local instance is recoverable without a separate seed command or manual database mutation.

### Alternatives Considered

- **Hard-code `master` / `master` in application logic**: Rejected because it conflicts with the repo’s secret-management rule.
- **Manual seed script**: Rejected because it weakens the guarantee that a fresh instance is immediately usable.
- **Database fixture or checked-in seed document**: Rejected because it is brittle and does not fit the runtime env-based secret model.

---

## Q5: Frontend Routing and Blank-Page Prevention

### Decision

Split routing into three explicit behaviors:

1. **Public auth routes** for `/login` and `/signup`
2. **Protected app routes** rendered only after auth checks succeed
3. **Explicit fallback routes** so unsupported or mistyped paths never render an empty shell

Also add an explicit redirect from `/batch-changes/:id` to `/batch-changes/:id/spec`, and ensure unsupported nav destinations resolve to a visible fallback page rather than blank content.

### Rationale

- The current frontend redirects to `/login` on `401`, but no `/login` route exists.
- `App.tsx` always renders the app shell even when route content is missing.
- The current navigation targets several undeclared routes (`/changesets`, `/templates`, `/audit`, and `/batch-changes/:id`), which currently produce empty main content.

### Alternatives Considered

- **Keep global shell rendering and only add `/login`**: Rejected because undeclared routes would still blank out the content area.
- **Remove all unsupported navigation immediately**: Rejected as a broader product/navigation change than needed for this feature.
- **Leave `window.location.href` redirect behavior untouched**: Rejected because route-aware auth guards are needed to preserve return paths and avoid silent blanks.

---

## Q6: Planning Artifacts and Test Pyramid

### Decision

Produce two contracts for Phase 1:

- `contracts/auth-api.yaml` for backend auth endpoints
- `contracts/route-access.md` for SPA route protection and layout behavior

Target the following test pyramid during implementation:

- **Backend unit**: password hashing, token issuance, bootstrap rules, validation helpers
- **Backend integration**: sign-up/sign-in/current-user endpoints against Mongo-backed persistence
- **Frontend unit/integration**: auth hook behavior, protected-route rendering, login/sign-up forms, 401 recovery, fallback routes
- **Functional**: Playwright browser flows for sign-in, sign-up, expired session, and unsupported-route rendering

### Rationale

- The repository already uses OpenAPI-style contracts for API work and markdown contracts for service/UI behavior.
- The constitution requires unit, integration, and functional coverage for new features.
- The current repo has only minimal backend and frontend tests and no checked-in Playwright auth flows, so this feature needs to establish the complete pyramid explicitly.

### Alternatives Considered

- **API contract only**: Rejected because the blank-page problem is also a UI route contract issue.
- **Unit tests only**: Rejected by the constitution and insufficient for auth + routing behavior.
- **Functional tests without backend integration tests**: Rejected because auth persistence and bootstrap behavior need service-boundary coverage.

---

## Summary of Decisions

| Decision Area | Chosen Approach | Why |
|---------------|-----------------|-----|
| Auth transport | JWT bearer tokens issued by auth endpoints | Fits existing middleware and frontend token handling |
| Identity model | Username-based local auth with SHA-256 prehashed bcrypt hash and role on `User` | Meets feature scope without overbuilding and supports long bootstrap secrets |
| Authorization model | `SUPER_USER` / `STANDARD` enum on user record | Smallest model that satisfies bootstrap admin access |
| Bootstrap strategy | Env-backed idempotent startup seeding of `master` / `master` in local dev | Guarantees first-run access while respecting secret-management rules |
| Routing fix | Public auth routes + protected app layout + explicit fallback routes | Removes both `/login` blanks and undeclared-route blanks |
| Phase 1 artifacts | Auth API contract + route-access contract + full test pyramid | Matches repo conventions and constitution gates |
