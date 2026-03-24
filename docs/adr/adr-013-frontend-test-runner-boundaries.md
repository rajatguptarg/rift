# ADR-013: Frontend Test Runner Boundaries

**Status**: Accepted  
**Date**: 2026-03-24  
**Deciders**: Rift Platform Team

---

## Context

Rift's frontend uses two different test tools for different jobs:

- Vitest for unit and integration coverage runs.
- Playwright for browser-driven end-to-end flows.

PR #4 exposed that the boundary was only implicit. `npm run test:coverage` used Vitest's default test discovery and collected `frontend/tests/e2e/auth-flows.spec.ts`, which imports Playwright's `test.describe()` API. That made the frontend CI job fail before any application regression was evaluated.

Local verification also depended on the host runtime's Web Storage implementation. Some Node runtimes expose a partial or incompatible `localStorage`, which made auth tests behave differently outside CI.

---

## Decision

Make the frontend test-runner boundary explicit:

- Vitest excludes `frontend/tests/e2e/**` from unit and coverage runs.
- Playwright specs remain in `frontend/tests/e2e/` and are executed only through `npm run test:e2e`.
- Shared Vitest setup provides an in-memory `localStorage` implementation so auth tests do not depend on host-specific storage behavior.

---

## Alternatives Considered

### Rename Playwright files to a non-Vitest pattern

**Rejected.** Renaming the files would reduce accidental collection, but the actual runner boundary would still live in naming conventions instead of explicit configuration.

### Run Playwright specs through Vitest

**Rejected.** Playwright's test DSL and lifecycle are separate from Vitest's execution model. Mixing them in the same run makes failures harder to interpret and breaks coverage-focused unit test jobs.

### Use the host runtime's `localStorage`

**Rejected.** That makes frontend auth tests depend on Node version and runtime flags instead of a deterministic test fixture.

---

## Consequences

### Positive

- Frontend coverage jobs only execute Vitest-managed suites.
- Playwright browser flows keep a dedicated invocation path.
- Local frontend test behavior is consistent across developer machines and CI.

### Negative / Trade-offs

- Frontend contributors need to know that `npm run test:coverage` and `npm run test:e2e` serve different purposes.
- Shared test setup now owns a small in-memory storage mock.

### Neutral

- Application code and API contracts are unchanged.
- Existing Playwright specs stay in the same directory.

---

## Implementation Notes

- `frontend/vite.config.ts` excludes `tests/e2e/**` from Vitest discovery.
- `frontend/src/test/setup.ts` defines the shared in-memory `localStorage` mock.
- `frontend/tests/unit/useAuth.test.tsx` resets only the auth token key between tests.
- `README.md` documents the split between Vitest and Playwright commands.

---

## References

- [README](../../README.md)
- [frontend/vite.config.ts](../../frontend/vite.config.ts)
- [frontend/src/test/setup.ts](../../frontend/src/test/setup.ts)
- [frontend/tests/e2e/auth-flows.spec.ts](../../frontend/tests/e2e/auth-flows.spec.ts)
