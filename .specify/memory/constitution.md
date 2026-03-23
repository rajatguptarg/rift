<!--
  Sync Impact Report
  ==================
  Version change: N/A → 1.0.0 (MAJOR — initial ratification)
  Modified principles: N/A (initial version)
  Added sections:
    - Core Principles (6 principles)
    - Development Workflow
    - Quality Gates
    - Governance
  Removed sections: N/A
  Templates requiring updates:
    - .specify/templates/plan-template.md ✅ no update needed
      (Constitution Check section is dynamic)
    - .specify/templates/spec-template.md ✅ no update needed
      (generic user-story structure compatible)
    - .specify/templates/tasks-template.md ✅ no update needed
      (testing phases align with Testing Pyramid principle)
  Follow-up TODOs: none
-->

# Rift Constitution

## Core Principles

### I. Test Coverage (NON-NEGOTIABLE)

- The project MUST maintain a minimum of **80% code coverage**
  at all times, measured across unit, integration, and
  functional test suites combined.
- All tests MUST pass on every commit pushed to a shared
  branch. A failing test suite is a blocking defect.
- Coverage regressions below 80% MUST be resolved before any
  pull request is merged.

**Rationale:** High coverage catches regressions early and
provides confidence during large-scale cross-repository
automation, which is the core value of Rift.

### II. Testing Pyramid

- Every feature MUST include tests at three levels, ordered by
  volume and speed:
  1. **Unit Tests** — isolated logic, no I/O, fast execution.
  2. **Integration Tests** — verify interactions between
     components, services, or data stores.
  3. **Functional Tests** — validate end-to-end user scenarios
     against the running system.
- Unit tests MUST form the largest share of the test suite.
  Integration tests MUST cover cross-boundary contracts.
  Functional tests MUST cover critical user journeys.
- New features without all three layers MUST NOT be merged
  unless a written justification is provided in the PR
  description.

**Rationale:** A layered testing strategy balances fast
feedback (unit) with realistic validation (functional) and
prevents gaps at component boundaries (integration).

### III. Secret Management

- All secrets, credentials, and sensitive configuration values
  MUST be loaded from environment variables at runtime.
- A `.env` file MUST be used for local development. This file
  MUST be listed in `.gitignore` and MUST NEVER be committed
  to version control.
- A `.env.example` file MUST be maintained in the repository
  root with placeholder keys (no real values) so that new
  contributors can set up their environment.
- Production deployments MUST inject secrets via the platform's
  native secret management (e.g., Kubernetes Secrets, cloud
  provider vaults) — never via checked-in files.

**Rationale:** Externalizing secrets prevents credential leaks
and aligns with OWASP best practices for configuration
management.

### IV. Documentation Currency

- Documentation, README, API contracts, and any artifacts
  related to a change MUST be updated in the **same pull
  request** that introduces the change.
- Stale documentation is treated as a defect. Reviewers MUST
  verify documentation accuracy as part of code review.
- API contracts (OpenAPI specs, gRPC protos, or equivalent)
  MUST reflect the current implementation at all times.

**Rationale:** Rift is a multi-team, multi-repository
automation platform. Drift between code and documentation
creates onboarding friction and integration errors.

### V. README Completeness

- The repository README MUST contain the following sections at
  a minimum:
  1. **About** — project purpose and overview.
  2. **Installation** — steps to install dependencies and the
     application.
  3. **Local Development** — how to set up and run locally.
  4. **Running** — how to start the application.
  5. **Testing** — how to execute the test suite.
  6. **Contributing** — contribution guidelines and workflow.
  7. **Architecture** — high-level architecture overview or
     link to architecture docs.
- The README MUST be updated whenever a change affects any of
  these sections.

**Rationale:** A complete README is the single entry point for
contributors and operators. Incomplete READMEs slow onboarding
and increase support burden.

### VI. Architectural Decision Records

- Every significant architectural decision MUST be recorded as
  an ADR under `docs/adr/`.
- ADR files MUST follow the naming convention
  `adr-XXX-<title>.md` where `XXX` is a zero-padded
  sequential number (e.g., `adr-001-use-mongodb.md`).
- Each ADR MUST include at minimum: **Context**, **Decision**,
  **Status**, and **Consequences**.
- ADRs MUST NOT be deleted. Superseded decisions MUST be marked
  with status `Superseded by adr-XXX`.

**Rationale:** ADRs provide a durable, reviewable record of
why the system is built the way it is, preventing repeated
debates and preserving institutional knowledge.

## Development Workflow

- All commits MUST follow **Conventional Commits** format with
  a mandatory Jira ticket reference:
  `type(scope?): subject [PROJECT-123]`.
- Branches MUST follow the pattern
  `<type>/<jira-ticket>-short-description`.
- Pull requests MUST include: what the change does, why it is
  needed, how it was tested, and a completion checklist.
- PRs MUST be scoped to a single logical change. Mixing
  unrelated work in one PR is not permitted.
- Force pushes to shared branches are prohibited unless
  explicitly authorized by a reviewer.

## Quality Gates

- Every pull request MUST pass the following gates before
  merge:
  1. **Build** — the project MUST compile/build without errors.
  2. **Lint** — code MUST pass all configured linting rules.
  3. **Test Suite** — all tests MUST pass with ≥80% coverage.
  4. **Code Review** — at least one approval from a qualified
     reviewer is required.
  5. **Documentation** — reviewers MUST verify that docs,
     README, and contracts are updated if affected.
- CI pipelines MUST enforce these gates automatically. Manual
  overrides MUST be documented with a justification.

## Governance

- This constitution supersedes all other project practices and
  guidelines when conflicts arise.
- Amendments to this constitution MUST be proposed via a pull
  request, reviewed by at least one project maintainer, and
  documented with a version bump.
- Versioning follows semantic versioning:
  - **MAJOR**: Principle removed or redefined in a
    backward-incompatible way.
  - **MINOR**: New principle or section added, or materially
    expanded guidance.
  - **PATCH**: Clarifications, wording, or non-semantic
    refinements.
- All PRs and code reviews MUST verify compliance with this
  constitution. Non-compliance MUST be resolved before merge.
- Complexity beyond what is required MUST be justified in
  writing (PR description or ADR).
- Use `CLAUDE.md` for runtime development guidance that
  supplements this constitution.

**Version**: 1.0.0 | **Ratified**: 2026-03-23 | **Last Amended**: 2026-03-23
