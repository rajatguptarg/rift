# Feature Specification: Rift Batch Changes Platform

**Feature Branch**: `001-batch-changes-platform`
**Created**: 2026-03-23
**Status**: Draft
**Input**: User description: "Rift Batch Changes — large-scale, cross-repository code automation platform enabling engineering teams to programmatically create, track, and manage code changes across hundreds or thousands of repositories simultaneously via a declarative YAML spec."

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Create and Execute a Batch Change via the Web UI (Priority: P1)

A platform engineer wants to update every Circle CI configuration across 200 repositories to use a new Docker Hub username. They navigate to the Batch Changes page, click "Create batch change", select the "Configuration" template, fill in the form fields (old username, new username), name the batch change, and click "Create". The system opens the Batch Spec Editor with a resolved preview of affected repositories. The engineer excludes two archived repositories, then clicks "Run batch spec". The execution screen shows real-time per-workspace logs, step-level diffs, and output variables. When execution completes, the engineer reviews proposed diffs and clicks "Apply" to finalize the batch change. The Changeset Dashboard now lists all generated changesets with their status.

**Why this priority**: This is the primary user journey and the core value loop of the entire product. Without server-side execution and a dashboard, no other feature delivers value.

**Independent Test**: Can be fully tested by creating a batch change from a template, executing it against a set of test repositories, and verifying changesets appear on the dashboard with correct diffs.

**Acceptance Scenarios**:

1. **Given** the user is authenticated and navigates to `/batch-changes`, **When** the user clicks "Create batch change", **Then** the system displays a template selection screen with curated templates and a "start from scratch" option.
2. **Given** the user selects a template and fills in validated form fields, **When** the user names the batch change and clicks "Create", **Then** the system opens the Batch Spec Editor with the generated YAML and a right-panel preview resolving affected repositories and workspaces.
3. **Given** the preview shows affected repositories, **When** the user excludes specific workspaces and clicks "Run batch spec", **Then** the execution screen displays real-time per-workspace status including logs, step diffs, output variables, and an execution timeline.
4. **Given** execution completes successfully, **When** the user reviews the proposed diffs and clicks "Apply", **Then** a batch change is created and the Changeset Dashboard displays all generated changesets with status (Open), CI check state (Pending), and review state (Pending).
5. **Given** execution encounters errors in some repositories, **When** skip-errors mode is enabled, **Then** the system continues execution for remaining repositories and flags failed workspaces with error details.

---

### User Story 2 — Publish and Track Changesets (Priority: P1)

After a batch change is applied, the platform engineer selects changesets on the dashboard and publishes them to the code host. They choose "Publish" for critical repositories (creating PRs), "Publish as Draft" for less-urgent ones, and "Push only" for repositories that need branch-only pushes. Over the following days, the dashboard shows real-time CI check results, review statuses, and merge states. The burndown chart shows progress toward full merge completion.

**Why this priority**: Publishing and tracking is the second half of the core value loop — without it, batch changes are preview-only with no real-world effect.

**Independent Test**: Can be tested by publishing a subset of changesets from an existing batch change and verifying PRs appear on the code host with correct title, body, branch, and commit message.

**Acceptance Scenarios**:

1. **Given** a batch change with unpublished changesets, **When** the user selects changesets and clicks "Publish", **Then** the system creates PRs/MRs on the respective code hosts with the title, body, branch, and commit message defined in the changeset template.
2. **Given** a batch change with unpublished changesets, **When** the user selects changesets and clicks "Publish as Draft", **Then** the system creates draft PRs on code hosts that support them.
3. **Given** a batch change with unpublished changesets, **When** the user selects changesets and clicks "Push only", **Then** the system pushes branches without creating PRs.
4. **Given** published changesets exist, **When** the code host reports CI check results, **Then** the dashboard updates changeset CI status in near-real-time (Passed/Failed/Pending).
5. **Given** published changesets exist, **When** reviewers approve, request changes, or merge PRs, **Then** the dashboard reflects the current review and merge status.
6. **Given** published changesets exist over time, **When** the user views the batch change, **Then** a burndown chart shows the proportion of changesets merged over time.

---

### User Story 3 — Create and Execute a Batch Change via CLI (Priority: P2)

A security engineer writes a batch spec YAML locally to pin all Docker image tags to specific digests across every repository. They run `rift batch preview -f spec.yaml` from the terminal. The CLI computes diffs and prints a preview URL. The engineer opens the URL in a browser, reviews the proposed changes, and clicks "Apply" in the UI. Alternatively, in a CI pipeline, they run `rift batch apply -f spec.yaml` to apply without a preview step.

**Why this priority**: CLI access is essential for power users and CI/CD integration, but depends on the core batch change and changeset infrastructure from P1.

**Independent Test**: Can be tested by running `rift batch preview` against test repositories and verifying the preview URL opens correctly with accurate diffs, then applying and checking changesets are created.

**Acceptance Scenarios**:

1. **Given** the user has installed and authenticated the rift CLI, **When** the user runs `rift batch preview -f spec.yaml`, **Then** the system computes diffs for all matched repositories and prints a preview URL.
2. **Given** a preview URL is opened in the browser, **When** the user reviews diffs and clicks "Apply", **Then** a batch change is created with changesets matching the spec.
3. **Given** the user runs `rift batch apply -f spec.yaml`, **When** the command completes, **Then** a batch change is created/updated directly without a preview step.
4. **Given** the user passes `--skip-errors`, **When** execution encounters individual repository failures, **Then** the CLI continues processing remaining repositories and reports failures at the end.
5. **Given** the user passes `--namespace org-name`, **When** the batch change is created, **Then** it belongs to the specified organization namespace.

---

### User Story 4 — Manage Credentials and Access Control (Priority: P2)

A site admin configures global credentials for GitHub and GitLab so that all users on the Rift instance can create batch changes without adding personal tokens. Individual users can also add their own personal access tokens scoped to specific code hosts. Users without read access to certain repositories see redacted information (no file paths, diffs, or repo names) in shared batch change views.

**Why this priority**: Credential management is a prerequisite for code host interaction and access control is critical for enterprise adoption, but it supports the core flows rather than being a standalone journey.

**Independent Test**: Can be tested by configuring global and per-user credentials, verifying batch changes succeed using each credential type, and verifying that unauthorized users see redacted data.

**Acceptance Scenarios**:

1. **Given** a site admin, **When** they configure global credentials for a code host, **Then** all users on the instance can create batch changes targeting that code host without personal tokens.
2. **Given** a user, **When** they add a personal access token for a code host, **Then** batch changes they create use their personal token.
3. **Given** a user without read access to a repository, **When** they view a batch change that includes that repository, **Then** the repository name, file paths, and diffs are redacted.
4. **Given** credentials are stored, **When** an admin audits credential usage, **Then** the system shows which credentials are scoped per user and per org.

---

### User Story 5 — Use Templates for Common Batch Changes (Priority: P3)

A site admin curates a library of batch spec templates covering common use cases: configuration updates, security patches, and code refactoring patterns. When a user creates a new batch change, they can pick a template, fill in regex-validated form fields, and have a complete batch spec generated automatically.

**Why this priority**: Templates accelerate adoption and standardize patterns, but the core batch change creation flow works without them.

**Independent Test**: Can be tested by creating a template, having a user select it during batch change creation, verifying form validation works, and confirming the generated YAML matches the template with filled parameters.

**Acceptance Scenarios**:

1. **Given** a site admin, **When** they create a batch spec template with typed form fields, **Then** the template appears in the template library for all users.
2. **Given** a user creating a batch change, **When** they select a template, **Then** the system displays the template's form fields with regex validation.
3. **Given** a user fills in all template fields correctly, **When** they proceed, **Then** the system generates a batch spec YAML with the parameter values substituted.
4. **Given** a user fills in a field with invalid input, **When** validation runs, **Then** the system shows a clear error message indicating the expected format.

---

### User Story 6 — Track Manually-Created Changesets (Priority: P3)

A staff engineer has an ongoing migration with 50 PRs already open across multiple repositories. They create a batch change in Rift and import these existing PRs so they can track review and merge progress from a single dashboard alongside any new PRs created by Rift.

**Why this priority**: Import/tracking of external changesets extends the platform's value to in-progress migrations but is not part of the core automation loop.

**Independent Test**: Can be tested by importing a known set of existing PRs into a batch change and verifying the dashboard correctly reflects their current status.

**Acceptance Scenarios**:

1. **Given** a user with an existing batch change, **When** they import external changeset URLs, **Then** the system adds them to the batch change and begins tracking their status.
2. **Given** imported changesets, **When** the code host reports status changes, **Then** the dashboard reflects CI, review, and merge state for imported changesets alongside Rift-created ones.
3. **Given** imported changesets, **When** the user views the burndown chart, **Then** imported changesets are included in the merged-over-time visualization.

---

### Edge Cases

- What happens when a batch spec targets zero repositories (the search query matches nothing)? The system must display a clear message: "No repositories matched the search query" and prevent execution.
- What happens when a code host rate-limits requests during bulk publishing? The system must back off, queue retries, and surface rate-limit status to the user.
- What happens when a user's personal access token expires or is revoked mid-execution? The system must halt code host operations for that user, flag the affected changesets, and prompt the user to re-authenticate.
- What happens when two batch changes target the same repository and branch? The system must detect the conflict and warn the user before apply.
- What happens when a workspace execution produces no diff (the change is a no-op for that repo)? The system must skip changeset creation for that workspace and indicate "no changes" in the preview.
- What happens when a monorepo workspace key matches projects that no longer exist? The system must flag missing workspaces and allow the user to acknowledge and continue.
- What happens when a batch change is applied but the underlying batch spec YAML is later modified? Re-running the spec should produce new changeset specs, and the reconciler should converge existing changesets toward the new desired state.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST accept a declarative batch spec (YAML) defining name, description, search query (`on`), execution steps, changeset template, and optional workspaces.
- **FR-002**: System MUST resolve the `on` search query to a list of target repositories and workspaces before execution.
- **FR-003**: System MUST execute batch spec steps in isolated containers against each matched repository/workspace, producing diffs and metadata.
- **FR-004**: System MUST combine execution diffs with the changeset template to produce changeset specs.
- **FR-005**: System MUST support server-side execution from the web UI without requiring a local environment.
- **FR-006**: System MUST support local/CI execution via the rift CLI, including `preview` and `apply` commands.
- **FR-007**: System MUST support a preview workflow where proposed diffs are displayed before finalization.
- **FR-008**: System MUST support an apply workflow that creates/updates the batch change directly.
- **FR-009**: System MUST support publishing changesets to code hosts as full PRs, draft PRs, or branch-only pushes.
- **FR-010**: System MUST support bulk actions (publish, archive, close) across multiple changesets simultaneously.
- **FR-011**: System MUST track changeset state (Open, Closed, Merged) in near-real-time via webhooks with polling fallback.
- **FR-012**: System MUST track CI check state (Passed, Failed, Pending) for each published changeset.
- **FR-013**: System MUST track review state (Approved, Changes Requested, Pending) for each published changeset.
- **FR-014**: System MUST display a burndown chart showing changeset merge progress over time.
- **FR-015**: System MUST display aggregate statistics: total batch changes, changesets merged, hours saved.
- **FR-016**: System MUST support filtering and searching across changesets within a batch change.
- **FR-017**: System MUST run a continuous reconciliation loop aligning changeset state on code hosts with desired state in changeset specs.
- **FR-018**: System MUST support GitHub, GitLab, Bitbucket Server/Data Center, Bitbucket Cloud, and Gerrit as code hosts.
- **FR-019**: System MUST store user credentials (personal access tokens) securely per user and per org, and support site-admin global credentials.
- **FR-020**: System MUST enforce namespace-based access control — batch changes belong to a user or org namespace.
- **FR-021**: System MUST redact repository names, file paths, and diffs for users without read access to the target repository.
- **FR-022**: System MUST support monorepo workspaces with per-workspace exclusion in the preview.
- **FR-023**: System MUST support a curated template library with regex-validated form fields for batch spec parameters.
- **FR-024**: System MUST support importing and tracking externally-created changesets within a batch change.
- **FR-025**: System MUST log all batch spec executions with step-level detail, output variables, and execution timelines for audit.
- **FR-026**: System MUST support a `--skip-errors` mode that continues execution past individual repository failures.
- **FR-027**: System MUST detect conflicts when two batch changes target the same repository and branch, and warn the user.

### Key Entities

- **Batch Change**: A named campaign representing a set of coordinated code changes across repositories. Belongs to a namespace (user or org). Contains a batch spec, execution runs, and changeset specs. Key attributes: name, description, namespace, state (open/closed), creator, creation date.
- **Batch Spec**: The declarative YAML definition of a batch change. Contains search query, execution steps, changeset template, and optional workspace configuration. Versioned — each edit creates a new spec version.
- **Changeset Spec**: The desired state for a single changeset (PR/MR), produced by combining an execution diff with the changeset template. Key attributes: target repository, branch, title, body, commit message, diff, desired publication state.
- **Changeset**: The actual PR/MR/change on a code host, tracked by Rift. Key attributes: external URL, state (Open/Closed/Merged), CI status, review status, publication type (full/draft/push-only), owning batch change.
- **Execution Run**: A record of executing a batch spec. Key attributes: start time, end time, status, per-workspace logs, step diffs, output variables, error details.
- **Workspace**: A target unit of execution — either a full repository or a sub-project within a monorepo. Key attributes: repository reference, path (for monorepo), inclusion/exclusion state.
- **Credential**: A stored authentication token for a code host. Key attributes: code host type, scope (user/org/global), encrypted token, expiry.
- **Template**: A reusable batch spec pattern with parameterized form fields. Key attributes: name, description, category, form field definitions (with regex validation), batch spec YAML with parameter placeholders.
- **Namespace**: An ownership scope — either a user or an organization. Determines visibility and access control for batch changes.

## Assumptions

- Rift already provides or will provide shared platform capabilities for identity/authentication, repository search, and repository mirror access.
- MVP targets a scale of up to 5,000 repositories per batch change and 500 concurrent workspace runners.
- The first production deployment is single-region active/passive.
- GitHub, GitLab, Bitbucket Server/Data Center, Bitbucket Cloud, and Gerrit are the supported code hosts for MVP. Perforce is beta. Phabricator is deferred.
- Container images used in batch spec steps are provided by the user or admin; Rift does not build images.
- Hours-saved estimates are calculated using a configurable formula (e.g., estimated manual time per changeset multiplied by changeset count).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create a batch change from template selection to applied changesets in under 10 minutes for batch changes targeting up to 100 repositories.
- **SC-002**: The system supports batch changes targeting 5,000 repositories with 25,000 workspace executions per day without degradation.
- **SC-003**: 95% of published changesets have their CI/review/merge status updated on the dashboard within 60 seconds of the event occurring on the code host.
- **SC-004**: The changeset merge rate (burndown slope) for active batch changes improves by 40% compared to manual PR management workflows.
- **SC-005**: 90% of batch spec executions complete without errors (excluding user-caused spec errors).
- **SC-006**: Users report the dashboard provides complete visibility into batch change progress, with no need to visit individual code host UIs to check status.
- **SC-007**: Average hours saved per batch change exceeds 50 hours (as computed by the platform's hours-saved formula).
