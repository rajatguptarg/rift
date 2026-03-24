# Implementation Plan: Restore Authenticated Access with Sign-In, Sign-Up, and Super User Bootstrap

**Branch**: `003-restore-auth-access` | **Date**: 2026-03-24 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/003-restore-auth-access/spec.md`

## Summary

Restore usable web access to Rift by adding first-party username/password authentication to the existing FastAPI + React stack, issuing JWT bearer tokens through dedicated auth endpoints, protecting application routes with an auth-aware layout, and bootstrapping a default super user from environment-backed local-development credentials. The design keeps CLI auth unchanged, removes blank-page failure modes by adding explicit public/protected/fallback routing, and adds unit, integration, and functional coverage for auth, bootstrap, and route-rendering behavior.

## Technical Context

**Language/Version**: Python 3.12 (backend), TypeScript 5.x (frontend)  
**Primary Dependencies**: FastAPI, Pydantic, Motor, python-jose, passlib[bcrypt], React 18, React Router 6, TanStack Query, axios  
**Storage**: MongoDB for user records and audit events; JWT bearer token held in browser auth state/local storage; existing Redis/Temporal/storage stack unchanged for this feature  
**Testing**: pytest + pytest-asyncio + pytest-cov (backend), Vitest + React Testing Library (frontend), Playwright for functional browser flows  
**Target Platform**: Local Docker stack and local hot-reload development on Linux containers + modern desktop browser  
**Project Type**: Web application (FastAPI API + React SPA)  
**Performance Goals**: Auth screen renders without blank states, sign-in completes in under 60 seconds, sign-up completes in under 2 minutes, protected-route redirects feel immediate to the user  
**Constraints**: Bootstrap credentials must be supplied via environment variables at runtime, existing CLI login behavior must remain unchanged, current Bearer-token middleware contract should be preserved, and every undefined or unauthorized navigation must render an explicit page instead of an empty shell  
**Scale/Scope**: Single Rift web instance with one bootstrap super user, self-service standard-user sign-up, and auth coverage for all current SPA entry points and primary product routes

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Research Gate

| # | Principle | Status | Evidence |
|---|-----------|--------|----------|
| I | Test Coverage ≥80% (NON-NEGOTIABLE) | ✅ PASS | Plan requires new backend + frontend tests across auth flows, bootstrap, and route rendering; implementation must contribute toward the 80% coverage target |
| II | Testing Pyramid | ✅ PASS | Planned layers: backend unit + integration, frontend unit/integration, Playwright browser flows for sign-in/sign-up and expired-session recovery |
| III | Secret Management | ✅ PASS | Bootstrap credentials and JWT secrets will be sourced from env vars and documented in `.env.example` / Compose, not hard-coded into runtime logic |
| IV | Documentation Currency | ✅ PASS | Plan produces research, data model, contracts, quickstart, README, and ADR updates in the same change set |
| V | README Completeness | ✅ PASS | README already contains required sections and will be refreshed to reference the new planning artifacts |
| VI | ADRs under `docs/adr/` | ✅ PASS | ADR-009 exists and will be kept current with the finalized auth/bootstrap design |

**Gate result: PASS — no blocking violations. Proceeding to Phase 0.**

### Post-Design Re-check

| # | Principle | Status | Evidence |
|---|-----------|--------|----------|
| I | Test Coverage ≥80% (NON-NEGOTIABLE) | ✅ PASS | Design defines concrete unit, integration, and functional auth coverage to add during implementation |
| II | Testing Pyramid | ✅ PASS | Data model, contracts, and quickstart all map to unit, integration, and Playwright verification paths |
| III | Secret Management | ✅ PASS | Bootstrap user values are environment-backed; contract and quickstart document `.env` / Compose usage rather than checked-in secrets |
| IV | Documentation Currency | ✅ PASS | Auth API contract, route-access contract, quickstart, README, and ADR were updated alongside the plan |
| V | README Completeness | ✅ PASS | README continues to cover overview, installation, development, running, testing, contributing, and architecture while now referencing the auth planning artifacts |
| VI | ADRs under `docs/adr/` | ✅ PASS | ADR-009 now captures the finalized auth bootstrap direction, including runtime secret handling and route separation |

**Post-design result: PASS — Phase 1 design remains constitution-compliant.**

## Project Structure

### Documentation (this feature)

```text
specs/003-restore-auth-access/
├── plan.md                  # This file
├── research.md              # Phase 0 output
├── data-model.md            # Phase 1 output
├── quickstart.md            # Phase 1 output
├── contracts/
│   ├── auth-api.yaml        # Auth API contract
│   └── route-access.md      # SPA route + layout contract
└── tasks.md                 # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── api/
│   │   ├── middleware/
│   │   │   └── auth.py              # Extend public-path handling + decoded claims
│   │   ├── routes/
│   │   │   └── auth.py              # New sign-in, sign-up, and current-user endpoints
│   │   └── dependencies.py          # Current-user + role-aware dependency helpers
│   ├── adapters/
│   │   └── mongo/
│   │       └── user_repo.py         # New user persistence and lookup operations
│   ├── models/
│   │   ├── auth.py                  # Request/response DTOs for auth endpoints
│   │   └── user.py                  # Extend user schema for username/password/role
│   ├── services/
│   │   ├── auth_service.py          # Sign-in, sign-up, JWT issuance, bootstrap logic
│   │   └── audit_service.py         # Record login events
│   ├── core/
│   │   └── config.py                # Bootstrap credential env vars
│   └── main.py                      # Register auth router + startup bootstrap hook
└── tests/
│   ├── unit/
│   │   ├── test_auth_models.py
│   │   └── test_auth_service.py
│   ├── integration/
│   │   └── test_auth_api.py
│   └── functional/
│       └── test_auth_flows.py

frontend/
├── src/
│   ├── App.tsx                      # Public/protected route split + fallback routes
│   ├── hooks/
│   │   └── useAuth.tsx              # Auth state hydration, sign-in/sign-up/sign-out helpers
│   ├── services/
│   │   └── api.ts                   # Route-aware 401 handling
│   ├── components/
│   │   ├── auth/
│   │   │   └── ProtectedRoute.tsx   # Gate protected content
│   │   └── layout/
│   │       └── AuthLayout.tsx       # Public auth-screen layout
│   └── pages/
│       ├── Auth/
│       │   ├── LoginPage.tsx
│       │   └── SignUpPage.tsx
│       └── System/
│           └── NotFoundPage.tsx
└── tests/
    ├── unit/
    │   ├── useAuth.test.tsx
    │   └── ProtectedRoute.test.tsx
    ├── integration/
    │   └── AuthPages.test.tsx
    └── e2e/
        └── auth-access.spec.ts
```

**Structure Decision**: Keep the existing backend/frontend split. Add a dedicated auth API route and Mongo repository on the backend, and add auth pages plus route guards on the frontend. Avoid introducing a separate identity service or standalone RBAC package because the feature scope is local web authentication restoration, not broader platform identity redesign.

## Complexity Tracking

No constitution violations or exceptional complexity require written justification beyond the ADR already recorded for local authentication bootstrap.
