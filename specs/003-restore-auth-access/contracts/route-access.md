# Contract: SPA Route Access and Rendering

**Feature**: `003-restore-auth-access`  
**Type**: UI route and layout contract  
**Date**: 2026-03-24

---

## Purpose

This contract defines how Rift routes behave for signed-out and signed-in users so the application never renders a blank page when authentication is missing, expired, or directed to an unsupported path.

---

## Layout Rules

| Layout | Used for | Chrome shown |
|--------|----------|--------------|
| `AuthLayout` | Public auth routes | No top app bar, no side nav |
| `AppLayout` | Protected product routes | Top app bar + side nav + content shell |
| `FallbackLayout` | Unknown routes | Public or protected presentation, but always explicit content |

**Invariant**: No route may render an empty `ContentShell` with no route body.

---

## Public Routes

| Route | Audience | Expected behavior |
|------|----------|-------------------|
| `/login` | Signed-out users | Render sign-in form and optional link to sign-up |
| `/signup` | Signed-out users | Render registration form for a standard user |

**Rules**

- If an authenticated user opens `/login` or `/signup`, redirect them to the remembered destination or `/batch-changes`.
- Public auth routes must preserve a `returnTo` value when the user was redirected from a protected route.

---

## Protected Routes

| Route | Behavior |
|------|----------|
| `/` | Redirect to `/batch-changes` after auth succeeds |
| `/batch-changes` | Render batch change list |
| `/batch-changes/new` | Render create flow |
| `/batch-changes/:id` | Redirect to `/batch-changes/:id/spec` |
| `/batch-changes/:id/spec` | Render batch spec editor |
| `/batch-changes/:id/runs/:runId` | Render execution view |
| `/batch-changes/:id/changesets` | Render changeset dashboard |
| `/credentials` | Render credential settings |

**Rules**

- Protected routes must not render until auth state has been checked.
- Missing or expired auth must clear the client token and route to `/login`.
- Protected content must render inside `AppLayout` only after auth succeeds.

---

## Unsupported and Unknown Routes

| Route case | Expected behavior |
|------------|-------------------|
| Known-but-not-yet-implemented nav targets such as `/changesets`, `/templates`, `/audit` | Render an explicit fallback page inside `AppLayout` instead of blank content |
| Any other unmatched path | Render a not-found page with clear recovery navigation |

**Invariant**: Unsupported or unknown routes must never fail silently.

---

## Auth Failure Behavior

| Trigger | Required behavior |
|---------|-------------------|
| API returns `401` during protected navigation | Clear local auth state and route to `/login` with the original destination remembered |
| User clicks sign out | Clear local auth state and render the login screen |
| Browser loads with a stale token | Validate auth before rendering protected pages; on failure, show login rather than blank content |

---

## Navigation Expectations

- The side navigation and top app bar are only visible after authentication succeeds.
- Route transitions from auth screens into protected routes should land on the originally requested page when available.
- A batch-change card click must never resolve to an undeclared route; `/batch-changes/:id` must always redirect to a concrete supported page.
