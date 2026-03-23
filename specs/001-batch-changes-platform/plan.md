# Implementation Plan: Rift Batch Changes Platform

**Branch**: `001-batch-changes-platform` | **Date**: 2026-03-23 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-batch-changes-platform/spec.md`

## Summary

Build the Rift Batch Changes platform — a declarative control plane with an ephemeral execution plane that enables engineering teams to create, preview, publish, and track large-scale code changes across thousands of repositories via a single YAML spec. The backend is Python/FastAPI with MongoDB persistence, Redis caching, and Temporal-driven workflow orchestration. The frontend is React/TypeScript. Containerized workspace execution runs on Kubernetes Jobs. A desired-state reconciliation loop keeps code host reality (PRs/MRs) aligned with internal changeset specs.

## Technical Context

**Language/Version**: Python 3.12 (backend), TypeScript 5.x (frontend/CLI)
**Primary Dependencies**: FastAPI, Pydantic, Motor (async MongoDB driver), Temporal Python SDK, React 18, React Router, TanStack Query, Tailwind CSS 3.x (utility-first styling), Material Symbols Outlined (icon font), Space Grotesk / Inter / Fira Code (Google Fonts)
**Storage**: MongoDB (primary), Redis (cache + coordination), S3-compatible object storage (logs/patches)
**Testing**: pytest + pytest-asyncio + pytest-cov (backend), Vitest + React Testing Library (frontend), Playwright (functional)
**Target Platform**: Kubernetes (Linux containers), single-region active/passive
**Project Type**: web-service (backend API + frontend SPA + CLI + async workers)
**Performance Goals**: API p95 < 200ms, preview start < 60s, dashboard load < 2s p95, webhook-to-UI freshness < 30s p95
**Constraints**: 99.9% API availability, code host rate limit compliance, runner isolation (non-root, no docker socket, egress deny-by-default)
**Scale/Scope**: 5,000 repos per batch change, 25,000 workspace executions/day, 500 concurrent runners

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| # | Principle | Status | Evidence |
|---|-----------|--------|----------|
| I | Test Coverage ≥80% (NON-NEGOTIABLE) | ✅ PASS | Plan includes unit/integration/functional test layers; CI gate enforces ≥80% coverage |
| II | Testing Pyramid (Unit → Integration → Functional) | ✅ PASS | Backend: pytest unit + integration (Motor/testcontainers) + functional (Playwright). Frontend: Vitest unit + integration + Playwright e2e |
| III | Secret Management (.env + env vars) | ✅ PASS | .env for local dev, .env.example committed, KMS-backed envelope encryption for credentials, Kubernetes Secrets for prod |
| IV | Documentation Currency | ✅ PASS | OpenAPI spec auto-generated from Pydantic models; docs updated in same PR as code |
| V | README Completeness (7 sections) | ✅ PASS | README structure planned with all 7 required sections |
| VI | ADRs under docs/adr/ | ✅ PASS | ADR directory exists; key decisions (MongoDB, Temporal, REST vs GraphQL) will be recorded |

**Gate result: PASS — no violations. Proceeding to Phase 0.**

## Project Structure

### Documentation (this feature)

```text
specs/001-batch-changes-platform/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── api.yaml         # OpenAPI 3.1 spec
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── api/                    # FastAPI routers and middleware
│   │   ├── routes/             # Route modules (batch_changes, changesets, credentials, templates, etc.)
│   │   ├── middleware/         # Auth, redaction, error handling
│   │   └── dependencies.py    # FastAPI dependency injection
│   ├── models/                 # Pydantic models (request/response + domain)
│   │   ├── batch_change.py
│   │   ├── batch_spec.py
│   │   ├── changeset.py
│   │   ├── changeset_spec.py
│   │   ├── credential.py
│   │   ├── execution.py
│   │   ├── template.py
│   │   └── namespace.py
│   ├── services/               # Business logic layer
│   │   ├── batch_change_service.py
│   │   ├── execution_orchestrator.py
│   │   ├── changeset_controller.py
│   │   ├── credential_service.py
│   │   ├── template_service.py
│   │   └── analytics_service.py
│   ├── adapters/               # External integrations
│   │   ├── code_hosts/         # GitHub, GitLab, Bitbucket, Gerrit adapters
│   │   ├── mongo/              # MongoDB repositories (data access)
│   │   ├── redis/              # Redis cache and coordination
│   │   ├── object_store/       # S3-compatible artifact storage
│   │   └── search/             # Repo search/mirror adapter
│   ├── workflows/              # Temporal workflow and activity definitions
│   │   ├── preview_workflow.py
│   │   ├── apply_workflow.py
│   │   └── activities/
│   ├── core/                   # Config, logging, encryption, errors
│   │   ├── config.py
│   │   ├── encryption.py
│   │   ├── logging.py
│   │   └── errors.py
│   └── main.py                 # FastAPI app entrypoint
├── tests/
│   ├── unit/                   # Isolated logic tests
│   ├── integration/            # Service + DB/cache tests
│   └── functional/             # End-to-end API + workflow tests
├── pyproject.toml
├── Dockerfile
└── .env.example

frontend/
├── src/
│   ├── components/             # Shared UI components
│   │   ├── ui/                 # Design-system primitive components
│   │   │   ├── Button.tsx          # Kinetic Pill — rounded-full, kinetic-gradient CTA
│   │   │   ├── TelemetryChip.tsx   # Mono-spaced status badge (LIVE · SYNCING · FAILED)
│   │   │   ├── IDECodePanel.tsx    # Code/YAML panel: surface-container-lowest + crosshatch bg
│   │   │   ├── Card.tsx            # Surface-shifted card (no dividers — bg shift only)
│   │   │   ├── ProgressBar.tsx     # 1px-height progress bar using primary-container fill
│   │   │   └── FrostedOverlay.tsx  # Frosted Obsidian — backdrop-blur 20px, 60% opacity
│   │   └── layout/             # App-shell layout primitives
│   │       ├── TopAppBar.tsx       # Fixed 64px bar — RIFT wordmark + search + icons
│   │       ├── SideNav.tsx         # Fixed 256px sidebar — Fira Code nav, CREATE pill CTA
│   │       └── ContentShell.tsx    # main: ml-64 + asymmetric padding
│   ├── pages/                  # Route-level page components
│   │   ├── BatchChangesList/       # Batch changes dashboard (hero stats + card grid)
│   │   ├── BatchChangeCreate/      # New batch-change form
│   │   ├── BatchSpecEditor/        # IDE-style split-pane YAML editor
│   │   ├── ExecutionView/          # Execution progress + log stream panel
│   │   ├── ChangesetDashboard/     # Per-batch changeset table + filter rail
│   │   └── CredentialSettings/    # Code host credential management
│   ├── theme/                  # Design tokens — single source of truth
│   │   ├── tokens.ts               # Typed color, font, spacing, radius constants
│   │   └── tailwind.config.ts      # Design-token Tailwind extension (mirrors DESIGN.md)
│   ├── services/               # API client layer
│   ├── hooks/                  # Custom React hooks
│   ├── types/                  # TypeScript type definitions
│   └── App.tsx
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/                    # Playwright tests
├── package.json
├── tsconfig.json
├── vite.config.ts
└── Dockerfile

cli/
├── src/                        # rift CLI source (TypeScript/Node)
│   ├── commands/
│   │   ├── login.ts
│   │   ├── batch-preview.ts
│   │   └── batch-apply.ts
│   ├── client/                 # API client
│   └── index.ts
├── tests/
├── package.json
└── tsconfig.json

helm/
├── Chart.yaml
├── values.yaml
└── charts/
    ├── frontend/
    ├── api/
    ├── workers/
    ├── runners/
    └── ingress/

docs/
├── adr/
├── product/
│   ├── PRD.md
│   └── HLD.md
└── design/

.github/
└── workflows/
    ├── ci-backend.yml
    ├── ci-frontend.yml
    ├── ci-helm.yml
    ├── cd-staging.yml
    └── cd-production.yml
```

**Structure Decision**: Web application layout (backend + frontend + CLI) selected based on the HLD's service-oriented architecture. Backend follows a layered architecture (API → Services → Adapters) with Temporal workflows as the orchestration layer. Frontend is a standalone React SPA. CLI is a separate TypeScript package sharing API contracts with the frontend.

## Frontend Design System

*Derived from `docs/design/DESIGN.md` and the four HTML mockups (batch-changes-dashboard, batch-spec-editor, changeset-management, marketing-landing-page). All frontend code must conform to these decisions.*

### Philosophy: "The Kinetic Monolith"
High-contrast Technical Noir aesthetic targeting elite engineers. Left-heavy asymmetric layouts, IDE-style layered panels, over-scaled headlines, and deliberate void space. Borders are prohibited — surface separation is achieved through tonal shifts only.

### Color Tokens

| Token | Hex | Role |
|---|---|---|
| `background` / `surface` | `#131313` | Base infinite void |
| `surface-container-lowest` | `#0E0E0E` | Recessed / negative-elevation panels |
| `surface-container-low` | `#1B1B1B` | Large background regions |
| `surface-container` | `#1F1F1F` | Standard containers |
| `surface-container-high` | `#2A2A2A` | Frosted overlays base |
| `surface-container-highest` | `#353535` | Active / elevated panels |
| `secondary-fixed` | `#1A1A2E` | Batch-change cards, inactive code panels |
| `primary-container` | `#FF5543` | CTA buttons, accent, progress bars |
| `primary` | `#FFB4A9` | Hover states, secondary accent |
| `primary-fixed` | `#FFDAD5` | Hover glow stroke on primary buttons |
| `tertiary` | `#45D8ED` | Syntax keywords, live-status indicators |
| `tertiary-container` | `#00A0B1` | RUNNING status chip background |
| `error-container` | `#93000A` | FAILED status chip background |
| `on-error-container` | `#FFDAD6` | FAILED chip text |
| `on-surface` / `on-background` | `#E2E2E2` | Body text |
| `on-surface-variant` | `#E4BEB8` | Secondary / meta text |
| `outline-variant` | `#5B403C` | Ghost-border (15% opacity) for dense tables |

### Typography

| Role | Font | Weight | Style rule |
|---|---|---|---|
| Display / Headlines | Space Grotesk | 800 ExtraBold | `tracking-widest`, `uppercase`, intentionally over-scaled |
| Body / Documentation | Inter | 400–600 | `body-md` density — technical manual feel |
| Metadata / Code / Status | Fira Code | 400–500 | All numbers, timestamps, version strings, status labels |

Loaded via Google Fonts: `Space Grotesk:wght@300;400;500;600;700;800`, `Inter:wght@300;400;500;600;700`, `Fira Code:wght@400;500`.

### Radius Rules

| Context | Value |
|---|---|
| All panels, cards, code panels, data tables | `0px` (sharp / none) |
| Buttons (Kinetic Pill), toggle groups, chips | `9999px` (`rounded-full`) |
| **Never use** | `4px`–`8px` rounded-md — forbidden |

### Component Primitives

#### `Button` — Kinetic Pill
```
Variant: primary
  bg: kinetic-gradient  (radial #FF5543 → #FFB4A9)
  text: on-primary-container (#5C0001)
  border: none | rounded-full | px-8 py-3
  hover: scale-105  |  active: scale-95
  hover stroke: 4px outer ring of primary-fixed (#FFDAD5)

Variant: ghost
  text: primary (#FFB4A9)
  border: outline-variant at 20% opacity | rounded-full
```

#### `TelemetryChip` — Status Badge
```
Font: Fira Code, 10px, uppercase, tracking-tighter
Structure: [colored dot] [STATUS TEXT]
States:
  RUNNING  → bg: tertiary-container  | text: on-tertiary-container
  FAILED   → bg: error-container     | text: on-error-container
  OPEN/LIVE → bg: primary-container  | text: on-primary-container
  SYNCING  → bg: secondary-container | text: secondary
No border, no rounded-md — pill (rounded-full) only
```

#### `IDECodePanel` — YAML / Log Viewer
```
bg: surface-container-lowest (#0E0E0E)
pattern: 1px crosshatch dots, 24px spacing, outline-variant at 10% opacity
thin scrollbar: 4px thumb at #353535 on #131313 track
syntax colors:
  keywords   → tertiary (#45D8ED)
  strings    → #A5D6FF
  YAML keys  → primary (#FFB4A9)
```

#### `FrostedOverlay` — Command Palette / Modals
```
bg: surface-container-high (#2A2A2A) at 60% opacity
backdrop-filter: blur(20px)  — "Frosted Obsidian"
ambient glow shadow: 64px blur, 5% primary (#FFB4A9)
```

#### `Card` — Batch Change Card
```
bg: secondary-fixed (#1A1A2E)  (default) | hover: #1F1F3D
no border, no divider lines
padding: p-6
border-radius: 0 (sharp)
left accent: border-l-4 border-primary-container for active/featured cards
```

### Layout Patterns

| Pattern | Specification |
|---|---|
| App shell | Fixed 64px `TopAppBar` + fixed 256px `SideNav` + scrollable `ContentShell` (`ml-64`) |
| Sidebar separation | No border — shift from `surface` (#131313) to `surface-container-low` (#1B1B1B) |
| Content asymmetry | Code/data panel: **65%** width · Docs/meta panel: **35%** — never equal columns |
| Section breathing room | `spacing-20` (4.5rem) between major sections |
| Dense data areas | `spacing-2` (0.4rem) row gap to maximise information density |
| Hero stat block | Left: Space Grotesk 7xl ExtraBold heading · Right: `secondary-fixed` impact-telemetry card |
| Table ghost borders | `outline-variant` at **15% opacity** — felt, not seen |

### Icon System
Material Symbols Outlined via Google Fonts CDN (`font-variation-settings: 'FILL' 0, 'wght' 400`). Rendered as text nodes with `.material-symbols-outlined` class. Interactive icons use `hover:text-primary` + `active:scale-90` transitions.

### Tailwind Config (`frontend/src/theme/tailwind.config.ts`)
All color tokens above must be registered as Tailwind color extensions matching the names in the table verbatim (kebab-case). Font families: `headline` → Space Grotesk, `body` → Inter, `label` → Inter, `mono` → Fira Code. Border-radius extensions: `DEFAULT: 1rem`, `lg: 2rem`, `xl: 3rem`, `full: 9999px`. The `kinetic-gradient` utility must be created as a Tailwind plugin.

## Complexity Tracking

> No constitution violations — this section is N/A.

## Constitution Re-Check (Post Phase 1 Design)

*GATE: Re-evaluated after Phase 1 design artifacts are complete.*

| # | Principle | Status | Post-Design Evidence |
|---|-----------|--------|---------------------|
| I | Test Coverage ≥80% (NON-NEGOTIABLE) | ✅ PASS | quickstart.md documents `pytest --cov-fail-under=80`; three test layers in project structure |
| II | Testing Pyramid | ✅ PASS | Unit (Pydantic models, state machines), Integration (Motor + testcontainers), Functional (Playwright) |
| III | Secret Management | ✅ PASS | Credential entity uses KMS envelope encryption; `.env` + `.env.example` in quickstart; no secrets in contracts |
| IV | Documentation Currency | ✅ PASS | contracts/api.yaml is OpenAPI source of truth; auto-generated from Pydantic models |
| V | README Completeness | ✅ PASS | quickstart.md covers all 7 required README sections |
| VI | ADRs | ✅ PASS | research.md documents 13 decisions ready for ADR conversion during implementation |

**Post-design gate result: PASS — proceeding to task generation.**
