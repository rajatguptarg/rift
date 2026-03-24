# Tasks: Restore Authenticated Access with Sign-In, Sign-Up, and Super User Bootstrap

**Input**: Design documents from `/specs/003-restore-auth-access/`  
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/auth-api.yaml ✓, contracts/route-access.md ✓, quickstart.md ✓

**Tests**: Included. The implementation plan, research, quickstart, and constitution require unit, integration, and functional coverage for this feature.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g. US1, US2, US3)
- Every task includes exact file paths in the description

## Path Conventions

- **Backend**: `backend/src/`, `backend/tests/`
- **Frontend**: `frontend/src/`, `frontend/tests/`
- **Docs/Specs**: `README.md`, `docs/adr/`, `specs/003-restore-auth-access/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare runtime configuration, contracts, and test scaffolding shared by all user stories

- [X] T001 Add bootstrap super-user runtime settings in `backend/src/core/config.py`, `.env.example`, and `docker-compose.yml`
- [X] T002 [P] Add auth testing entry points and browser-test wiring in `backend/tests/integration/conftest.py`, `backend/tests/functional/__init__.py`, and `frontend/package.json`
- [X] T003 [P] Sync shared auth/session API types from the contracts into `frontend/src/types/api.ts`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core auth infrastructure that MUST be complete before any user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Expand persisted user, role, and session models in `backend/src/models/user.py`
- [X] T005 [P] Implement Mongo-backed user persistence with username uniqueness support in `backend/src/adapters/mongo/user_repo.py`
- [X] T006 [P] Implement password hashing, JWT issuance, and session assembly helpers in `backend/src/services/auth_service.py`
- [X] T007 Update bearer-token validation and persisted current-user resolution in `backend/src/api/middleware/auth.py` and `backend/src/api/dependencies.py`
- [X] T008 [P] Refactor frontend auth state to support hydration, redirect intent, and role-aware session data in `frontend/src/hooks/useAuth.tsx`
- [X] T009 [P] Create reusable auth layout and form primitives in `frontend/src/components/auth/AuthLayout.tsx` and `frontend/src/components/auth/AuthForm.tsx`
- [X] T010 [P] Create visible unsupported-route fallback UI in `frontend/src/pages/NotFound/index.tsx`
- [X] T011 Wire public-auth, protected-app, and wildcard route skeletons in `frontend/src/App.tsx`

**Checkpoint**: Foundation ready. User story implementation can now begin.

---

## Phase 3: User Story 1 - Signed-Out User Can Sign In and Reach the App (Priority: P1) 🎯 MVP

**Goal**: Restore access for existing users by providing a usable login experience and protected-route rendering with no blank pages.

**Independent Test**: Open a protected route while signed out, confirm `/login` renders instead of a blank page, sign in successfully, return to the original route, and confirm invalid credentials stay on the login screen with a visible error.

### Tests for User Story 1

- [X] T012 [P] [US1] Add password verification and session issuance unit coverage in `backend/tests/unit/test_auth_service.py`
- [X] T013 [P] [US1] Add auth-state hydration and redirect-intent unit coverage in `frontend/tests/unit/useAuth.test.tsx`
- [X] T014 [P] [US1] Add auth API contract coverage for `POST /auth/sign-in` and `GET /auth/me` in `backend/tests/integration/test_auth_routes.py`
- [X] T015 [P] [US1] Add protected-route redirect and route-fallback coverage from `contracts/route-access.md` in `frontend/tests/integration/auth-routing.test.tsx`
- [X] T016 [P] [US1] Add sign-in return-to-route browser flow coverage in `frontend/tests/e2e/auth-flows.spec.ts`

### Implementation for User Story 1

- [X] T017 [US1] Implement sign-in and current-session response shaping in `backend/src/models/user.py` and `backend/src/services/auth_service.py`
- [X] T018 [US1] Implement `POST /auth/sign-in` and `GET /auth/me` in `backend/src/api/routes/auth.py`
- [X] T019 [US1] Register auth routes and public-path exemptions in `backend/src/main.py` and `backend/src/api/middleware/auth.py`
- [X] T020 [US1] Implement the login experience and inline invalid-credential states in `frontend/src/pages/Auth/LoginPage.tsx`
- [X] T021 [US1] Implement session hydration, 401 recovery, and redirect-intent handling in `frontend/src/hooks/useAuth.tsx` and `frontend/src/services/api.ts`
- [X] T022 [US1] Complete protected-route rendering and no-blank fallback behavior in `frontend/src/App.tsx` and `frontend/src/pages/NotFound/index.tsx`
- [X] T023 [US1] Record successful sign-in audit events in `backend/src/api/routes/auth.py` and `backend/src/services/audit_service.py`

**Checkpoint**: User Story 1 is independently functional and can serve as the MVP.

---

## Phase 4: User Story 2 - New User Can Create an Account and Start Using Rift (Priority: P2)

**Goal**: Allow new users to register through the web UI, create a standard account, and enter the app without operator help.

**Independent Test**: Open `/signup`, create a new user, confirm a duplicate username is rejected with a visible validation error, and verify a successful sign-up lands on `/batch-changes` with usable page content.

### Tests for User Story 2

- [X] T024 [P] [US2] Add sign-up validation and standard-role unit coverage in `backend/tests/unit/test_auth_service.py`
- [X] T025 [P] [US2] Add auth API contract coverage for `POST /auth/sign-up` and duplicate usernames in `backend/tests/integration/test_auth_routes.py`
- [X] T026 [P] [US2] Add sign-up page rendering and validation coverage in `frontend/tests/integration/auth-routing.test.tsx`
- [X] T027 [P] [US2] Add self-service sign-up browser flow coverage in `frontend/tests/e2e/auth-flows.spec.ts`

### Implementation for User Story 2

- [X] T028 [US2] Implement standard-user defaults and duplicate-username handling in `backend/src/services/auth_service.py` and `backend/src/adapters/mongo/user_repo.py`
- [X] T029 [US2] Implement `POST /auth/sign-up` in `backend/src/api/routes/auth.py`
- [X] T030 [US2] Implement the sign-up page and field-level validation states in `frontend/src/pages/Auth/SignUpPage.tsx`
- [X] T031 [US2] Share sign-in/sign-up form behavior across auth routes in `frontend/src/components/auth/AuthForm.tsx`
- [X] T032 [US2] Complete post-sign-up session creation and default landing redirects in `frontend/src/hooks/useAuth.tsx` and `frontend/src/App.tsx`

**Checkpoint**: User Story 2 is independently functional once a new user can register and enter the app successfully.

---

## Phase 5: User Story 3 - Operator Can Recover Administration with the Bootstrap Super User (Priority: P3)

**Goal**: Guarantee that a clean local environment boots with a single super-user account that can sign in and reach administrative pages.

**Independent Test**: Start Rift in a clean local environment, sign in with `master` / `master`, verify access to `/credentials`, and confirm restarting the app does not create duplicate bootstrap users.

### Tests for User Story 3

- [X] T033 [P] [US3] Add bootstrap seed creation and idempotency unit coverage in `backend/tests/unit/test_bootstrap_service.py`
- [X] T034 [P] [US3] Add bootstrap idempotency and role-resolution integration coverage in `backend/tests/integration/test_bootstrap_auth.py`
- [X] T035 [P] [US3] Add clean-environment bootstrap login functional coverage in `backend/tests/functional/test_auth_journeys.py`

### Implementation for User Story 3

- [X] T036 [US3] Implement bootstrap super-user seeding in `backend/src/services/bootstrap_service.py`
- [X] T037 [US3] Invoke bootstrap seeding during API startup in `backend/src/main.py`
- [X] T038 [US3] Enforce persisted super-user access checks for administrative surfaces in `backend/src/api/dependencies.py` and `backend/src/api/routes/credentials.py`
- [X] T039 [US3] Surface bootstrap-admin navigation and credential-page access states in `frontend/src/components/layout/SideNav.tsx` and `frontend/src/pages/CredentialSettings/index.tsx`

**Checkpoint**: User Story 3 is independently functional once `master` / `master` works on a clean startup and admin access remains stable across restarts.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final contract, documentation, and validation work that spans multiple stories

- [X] T040 [P] Update runtime auth setup documentation in `README.md` and `.env.example`
- [X] T041 [P] Reconcile implementation details with architecture and operator docs in `docs/adr/adr-009-local-auth-bootstrap.md` and `specs/003-restore-auth-access/quickstart.md`
- [X] T042 Verify and align final auth contracts, route-access docs, and test commands in `specs/003-restore-auth-access/contracts/auth-api.yaml`, `specs/003-restore-auth-access/contracts/route-access.md`, `backend/pyproject.toml`, and `frontend/package.json`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies; can start immediately.
- **Phase 2 (Foundational)**: Depends on Phase 1; blocks all story work.
- **Phase 3 (US1)**: Depends on Phase 2; delivers the MVP.
- **Phase 4 (US2)**: Depends on Phase 2 and reuses the session/auth route structure established in US1.
- **Phase 5 (US3)**: Depends on Phase 2 and reuses the sign-in/session plumbing from US1.
- **Phase 6 (Polish)**: Depends on all completed story work.

### User Story Dependency Graph

```text
Phase 1 (Setup)
  -> Phase 2 (Foundational)
      -> Phase 3 (US1: Sign-In + Protected Routes) [MVP]
          -> Phase 4 (US2: Sign-Up)
          -> Phase 5 (US3: Bootstrap Super User)
      -> Phase 6 (Polish) after desired stories complete
```

### Story Completion Order

- **US1 (P1)** should be completed first because it restores core access and provides the shared auth/session path used by the later stories.
- **US2 (P2)** extends the same auth flow with self-service account creation.
- **US3 (P3)** finishes the local-operability slice with bootstrap admin seeding and admin-only access checks.

---

## Parallel Opportunities

### Phase 1

- T002 and T003 can run in parallel after T001.

### Phase 2

- T005, T006, T008, T009, and T010 can run in parallel once T004 is defined.
- T011 depends on T008, T009, and T010.

### User Story 1

- T012, T013, T014, T015, and T016 can run in parallel.
- T020 and T021 can proceed in parallel after T018 and T019 define the backend session contract.

### User Story 2

- T024, T025, T026, and T027 can run in parallel.
- T030 and T031 can proceed in parallel after T029 establishes the backend sign-up contract.

### User Story 3

- T033, T034, and T035 can run in parallel.
- T038 and T039 can proceed in parallel after T036 and T037 establish bootstrap role data.

---

## Parallel Example: User Story 1

```bash
# Launch US1 tests together:
Task: "Add password verification and session issuance unit coverage in backend/tests/unit/test_auth_service.py"
Task: "Add auth-state hydration and redirect-intent unit coverage in frontend/tests/unit/useAuth.test.tsx"
Task: "Add auth API contract coverage for POST /auth/sign-in and GET /auth/me in backend/tests/integration/test_auth_routes.py"
Task: "Add protected-route redirect and route-fallback coverage in frontend/tests/integration/auth-routing.test.tsx"
Task: "Add sign-in return-to-route browser flow coverage in frontend/tests/e2e/auth-flows.spec.ts"
```

```bash
# Launch independent UI/backend implementation tracks after the route contract is clear:
Task: "Implement the login experience and inline invalid-credential states in frontend/src/pages/Auth/LoginPage.tsx"
Task: "Implement session hydration, 401 recovery, and redirect-intent handling in frontend/src/hooks/useAuth.tsx and frontend/src/services/api.ts"
```

## Parallel Example: User Story 2

```bash
# Launch US2 tests together:
Task: "Add sign-up validation and standard-role unit coverage in backend/tests/unit/test_auth_service.py"
Task: "Add auth API contract coverage for POST /auth/sign-up and duplicate usernames in backend/tests/integration/test_auth_routes.py"
Task: "Add sign-up page rendering and validation coverage in frontend/tests/integration/auth-routing.test.tsx"
Task: "Add self-service sign-up browser flow coverage in frontend/tests/e2e/auth-flows.spec.ts"
```

```bash
# Launch UI tasks in parallel once backend sign-up contract exists:
Task: "Implement the sign-up page and field-level validation states in frontend/src/pages/Auth/SignUpPage.tsx"
Task: "Share sign-in/sign-up form behavior across auth routes in frontend/src/components/auth/AuthForm.tsx"
```

## Parallel Example: User Story 3

```bash
# Launch US3 tests together:
Task: "Add bootstrap seed creation and idempotency unit coverage in backend/tests/unit/test_bootstrap_service.py"
Task: "Add bootstrap idempotency and role-resolution integration coverage in backend/tests/integration/test_bootstrap_auth.py"
Task: "Add clean-environment bootstrap login functional coverage in backend/tests/functional/test_auth_journeys.py"
```

```bash
# Launch admin-surface follow-up work in parallel after bootstrap seeding exists:
Task: "Enforce persisted super-user access checks for administrative surfaces in backend/src/api/dependencies.py and backend/src/api/routes/credentials.py"
Task: "Surface bootstrap-admin navigation and credential-page access states in frontend/src/components/layout/SideNav.tsx and frontend/src/pages/CredentialSettings/index.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational.
3. Complete Phase 3: User Story 1.
4. Validate the independent test for US1 before moving on.
5. Demo or ship the restored sign-in flow as the MVP.

### Incremental Delivery

1. Finish Setup + Foundational once.
2. Deliver **US1** to restore sign-in and eliminate blank pages.
3. Deliver **US2** to add self-service sign-up.
4. Deliver **US3** to finish local bootstrap-admin recovery.
5. Run Phase 6 to reconcile docs, contracts, and validation.

### Suggested MVP Scope

- **MVP**: Phase 1 + Phase 2 + Phase 3 (US1 only)
- This is the smallest slice that restores usable access to Rift and fixes the blank-page regression.

---

## Notes

- Every task follows the required checklist format: checkbox, task ID, optional `[P]`, required story label for story phases, and explicit file paths.
- Story phases are sized so each story can be validated independently once its tasks are complete.
- Cross-story file overlap is intentionally minimized outside the shared auth/session files noted in the dependency section.
