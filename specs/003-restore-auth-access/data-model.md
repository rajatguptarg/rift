# Data Model: Restore Authenticated Access with Sign-In, Sign-Up, and Super User Bootstrap

**Feature**: `003-restore-auth-access`  
**Phase**: 1 — Design  
**Date**: 2026-03-24

## Overview

This feature adds first-party web authentication to Rift. It introduces a persistent local-auth user record, a lightweight role model, and a runtime session representation backed by JWT claims. The model is intentionally minimal: it solves local sign-in, sign-up, super-user bootstrap, and protected-route rendering without expanding into full RBAC or external identity integration.

---

## Relationship Summary

```text
AccessRole (enum) ── assigned to ──▶ UserAccount
UserAccount ── authenticates via ──▶ AuthSession (JWT, runtime)
UserAccount ── triggers ──▶ AuditEvent (LOGIN)
UserAccount ── derives personal namespace via existing convention ──▶ ns_{user_id}
```

---

## Entities

### UserAccount

Persistent MongoDB document representing a Rift web user.

| Field | Type | Description |
|-------|------|-------------|
| `id` | string (`usr_...`) | Stable user identifier used in tokens and namespace derivation |
| `username` | string | Unique sign-in identifier; stored and compared in normalized lowercase form |
| `display_name` | string | Human-readable name shown in the UI |
| `email` | string? | Optional contact field; not required for sign-in |
| `password_hash` | string | SHA-256 prehashed bcrypt hash; raw password is never stored and legacy raw bcrypt hashes remain readable |
| `role` | enum (`SUPER_USER`, `STANDARD`) | Global authorization level for this feature |
| `auth_subject` | string | Local auth subject in the form `local:{username}` |
| `bootstrap_managed` | boolean | `true` for the env-seeded default super user |
| `last_login_at` | datetime? | Updated after successful sign-in |
| `created_at` | datetime | Creation timestamp |
| `updated_at` | datetime | Last mutation timestamp |

**Validation rules**

- `username` is required, 3-32 characters, lowercase-normalized, and unique
- `username` may contain letters, numbers, `_`, `-`, and `.`
- `display_name` is required, 1-80 characters after trimming
- `email`, when provided, must be a valid email address
- Password input must be at least 6 characters so the required bootstrap password `master` remains valid for local development
- Password hashing uses a SHA-256 prehash before bcrypt so secrets longer than 72 bytes remain valid
- `bootstrap_managed=true` implies `role=SUPER_USER`

**Lifecycle**

```text
sign-up request
    │
    ▼
[create UserAccount as STANDARD]
    │
    ├──▶ successful sign-in updates last_login_at
    └──▶ future admin action may elevate role (out of current feature scope)
```

---

### AccessRole

Reference role model used for authorization decisions. This is represented as an enum on `UserAccount`, not as a separate collection.

| Value | Purpose | Core Capabilities |
|-------|---------|-------------------|
| `SUPER_USER` | Bootstrap/global administrator | Access all web areas, manage privileged actions, recover a fresh local instance |
| `STANDARD` | Default self-service account | Use standard Rift web flows with no bootstrap/admin elevation by default |

**Constraints**

- Every user must have exactly one role
- Self-service sign-up always creates `STANDARD`
- The default `master` account is always `SUPER_USER`

---

### AuthSession

Runtime representation of an authenticated Rift browser session. It is transported as a JWT bearer token and is not stored as a server-side session record in this feature.

| Field | Type | Description |
|-------|------|-------------|
| `access_token` | string | Signed JWT returned after sign-in/sign-up |
| `token_type` | string | Always `Bearer` |
| `user_id` | string | Mirrors `UserAccount.id` |
| `username` | string | Current user identifier for client hydration |
| `role` | enum | Authorization level surfaced to API dependencies and UI |
| `email` | string? | Optional profile field for client hydration |
| `issued_at` | datetime | Token issuance time |
| `expires_at` | datetime | Expiration time derived from configured JWT lifetime |

**State transitions**

```text
[No session]
    │ sign-in/sign-up success
    ▼
[Active session]
    │
    ├──▶ user sign-out        ──▶ [No session]
    └──▶ token expiry / 401   ──▶ [Expired session] ── re-authenticate ──▶ [Active session]
```

**Constraints**

- Client stores only the token and derived user summary needed for rendering
- Any invalid or expired token must be discarded before protected content renders
- `role` and `user_id` claims must match the current persistent user record at issuance time

---

### BootstrapAuthConfig

Runtime-only configuration that defines the default local administrative account.

| Field | Type | Source | Description |
|-------|------|--------|-------------|
| `username` | string | env var | Default bootstrap username (`master` in local dev) |
| `password` | string | env var | Default bootstrap password (`master` in local dev) |
| `display_name` | string | env var / default | Friendly label for the bootstrap user |

**Constraints**

- Values are read from environment variables at startup
- Startup must create the bootstrap user only when no matching bootstrap-managed account exists
- Repeated startups must never create duplicate bootstrap users

---

## Derived / Existing Relationships

- The existing namespace convention (`ns_{user_id}`) can continue to derive a personal namespace for newly signed-up users without adding a new namespace schema in this feature.
- Successful sign-in should record an `AuditEvent` with action `LOGIN` using the existing audit model.
- No separate persisted session collection is required for this feature; JWT remains the sole session transport.

---

## No Additional Collections Required

This design can be implemented with one new persistent MongoDB collection for users (or an equivalent addition if user storage already exists outside the checked-in code) plus the existing audit collection. Roles remain an enum, and sessions remain stateless JWT payloads.
