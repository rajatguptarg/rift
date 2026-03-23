# Data Model: Rift Batch Changes Platform

**Date**: 2026-03-23
**Source**: HLD Section 11 (MongoDB Data Model), spec.md Key Entities

## Entity Relationship Overview

```
User ──┬── owns ──▶ Namespace (USER)
       └── member of ──▶ Organization ── owns ──▶ Namespace (ORG)

Namespace ── owns ──▶ BatchChange ── has ──▶ BatchSpec (versioned, 1:N)
                           │
                           ├── has ──▶ BatchRun (1:N)
                           │              └── has ──▶ WorkspaceExecution (1:N)
                           │                             └── has ──▶ ExecutionStep (1:N)
                           │
                           ├── has ──▶ ChangesetSpec (1:N)
                           │              └── tracked by ──▶ Changeset (1:1)
                           │                                    └── has ──▶ ChangesetEvent (1:N)
                           │
                           └── uses ──▶ Template (optional)

Credential ── scoped to ──▶ Namespace + CodeHost
Repository ── registered from ──▶ CodeHost
AuditEvent ── records actions on ──▶ any resource
```

## Entities

### User

| Field | Type | Description |
|-------|------|-------------|
| id | string (usr_...) | Unique identifier |
| email | string | User email |
| display_name | string | Display name |
| auth_subject | string | External auth provider subject |
| created_at | datetime | Creation timestamp |

### Organization

| Field | Type | Description |
|-------|------|-------------|
| id | string (org_...) | Unique identifier |
| name | string | Organization name |
| slug | string | URL-safe slug |
| created_at | datetime | Creation timestamp |

### Namespace

| Field | Type | Description |
|-------|------|-------------|
| id | string (ns_...) | Unique identifier |
| kind | enum (USER, ORG) | Namespace type |
| owner_user_id | string? | User owner (when kind=USER) |
| owner_org_id | string? | Org owner (when kind=ORG) |
| visibility_policy | object | Redaction and visibility rules |

**Relationships**: Owns BatchChange, Credential, Template (namespace-scoped).

### CodeHost

| Field | Type | Description |
|-------|------|-------------|
| id | string (ch_...) | Unique identifier |
| kind | enum (GITHUB, GITLAB, BITBUCKET_SERVER, BITBUCKET_CLOUD, GERRIT) | Host type |
| base_url | string | Host base URL |
| display_name | string | Human-readable name |
| is_active | boolean | Whether host is enabled |

### Repository

| Field | Type | Description |
|-------|------|-------------|
| id | string (repo_...) | Unique identifier |
| external_repo_ref | string | Full external reference (e.g., github.com/acme/service-a) |
| code_host_id | string | FK to CodeHost |
| name | string | Short name (e.g., acme/service-a) |
| default_branch | string | Default branch name |
| mirror_ref | string | Internal mirror reference |
| visibility | enum (PUBLIC, PRIVATE) | Repo visibility |
| last_synced_at | datetime | Last sync timestamp |

### Credential

| Field | Type | Description |
|-------|------|-------------|
| id | string (cred_...) | Unique identifier |
| namespace_id | string | FK to Namespace |
| user_id | string? | FK to User (null for global) |
| code_host_id | string | FK to CodeHost |
| encrypted_secret | string | KMS-encrypted token ciphertext |
| kms_key_ref | string | KMS key reference |
| scopes | string[] | Token permission scopes |
| created_at | datetime | Creation timestamp |
| rotated_at | datetime? | Last rotation timestamp |

**Constraints**: Unique per (namespace_id, user_id, code_host_id).

### Template

| Field | Type | Description |
|-------|------|-------------|
| id | string (tpl_...) | Unique identifier |
| namespace_id | string? | FK to Namespace (null = global/built-in) |
| name | string | Template name |
| description | string | Template description |
| spec_template_yaml | string | YAML template with parameter placeholders |
| form_schema | object | JSON Schema for form fields |
| validation_rules | map<string, string> | Regex validation per field |
| is_builtin | boolean | Whether built-in |
| is_active | boolean | Whether available for selection |

### BatchChange

| Field | Type | Description |
|-------|------|-------------|
| id | string (bc_...) | Unique identifier |
| namespace_id | string | FK to Namespace |
| name | string | Batch change name |
| description | string | Batch change description |
| source_mode | enum (UI, CLI) | How it was created |
| state | enum | See State Model below |
| created_by | string | FK to User |
| active_spec_id | string | FK to current BatchSpec |
| created_at | datetime | Creation timestamp |
| updated_at | datetime | Last update timestamp |
| archived_at | datetime? | Archive timestamp |
| version | integer | Optimistic concurrency version |

**State values**: DRAFT, PREVIEW_RUNNING, PREVIEW_READY, APPLYING, ACTIVE, PAUSED, ARCHIVED, FAILED

### BatchSpec

| Field | Type | Description |
|-------|------|-------------|
| id | string (bs_...) | Unique identifier |
| batch_change_id | string | FK to BatchChange |
| spec_yaml | string | Full YAML content |
| spec_hash | string | SHA-256 of YAML for dedup |
| template_bindings | map<string, string>? | Resolved template parameters |
| search_query | string | Extracted `on` query |
| created_at | datetime | Creation timestamp |

**Relationships**: Belongs to BatchChange (N:1).

### BatchRun

| Field | Type | Description |
|-------|------|-------------|
| id | string (br_...) | Unique identifier |
| batch_change_id | string | FK to BatchChange |
| batch_spec_id | string | FK to BatchSpec |
| mode | enum (PREVIEW, APPLY) | Execution mode |
| state | enum (QUEUED, RUNNING, COMPLETED, FAILED, CANCELLED) | Run state |
| skip_errors | boolean | Whether to continue past failures |
| requested_by | string | FK to User |
| started_at | datetime | Start timestamp |
| completed_at | datetime? | Completion timestamp |
| summary | object | Aggregate counts (total, succeeded, failed, pending) |

### WorkspaceExecution

| Field | Type | Description |
|-------|------|-------------|
| id | string (we_...) | Unique identifier |
| batch_run_id | string | FK to BatchRun |
| repository_id | string | FK to Repository |
| workspace_path | string | Path within repo (/ for full repo) |
| state | enum (QUEUED, RUNNING, SUCCEEDED, FAILED, CANCELLED, SKIPPED) | Execution state |
| exclusion_reason | string? | Why excluded (if excluded) |
| runner_job_ref | string? | Kubernetes Job reference |
| started_at | datetime? | Start timestamp |
| completed_at | datetime? | Completion timestamp |

### ExecutionStep

| Field | Type | Description |
|-------|------|-------------|
| id | string (step_...) | Unique identifier |
| workspace_execution_id | string | FK to WorkspaceExecution |
| step_index | integer | Order within execution |
| container_image | string | Docker image used |
| command_text | string | Shell command executed |
| exit_code | integer? | Process exit code |
| started_at | datetime | Step start timestamp |
| completed_at | datetime? | Step completion timestamp |
| stdout_artifact_key | string? | Object storage key for stdout |
| stderr_artifact_key | string? | Object storage key for stderr |
| diff_artifact_key | string? | Object storage key for diff |
| outputs | map<string, string> | Declared output variables |

### ChangesetSpec

| Field | Type | Description |
|-------|------|-------------|
| id | string (css_...) | Unique identifier |
| batch_change_id | string | FK to BatchChange |
| workspace_execution_id | string? | FK to WorkspaceExecution (null for imports) |
| repository_id | string | FK to Repository |
| workspace_path | string | Path within repo |
| base_rev | string | Base revision hash |
| head_ref | string | Head branch reference |
| publication_mode | enum (UNPUBLISHED, PUBLISH, DRAFT, PUSH_ONLY) | Desired pub state |
| title_rendered | string | Rendered PR title |
| body_rendered | string | Rendered PR body |
| commit_message_rendered | string | Rendered commit message |
| branch_name_rendered | string | Rendered branch name |
| patch_artifact_key | string? | Object storage key for patch |
| spec_fingerprint | string | Content hash for dedup/reconciliation |
| state | enum | See State Model below |
| created_at | datetime | Creation timestamp |

**State values**: UNPUBLISHED, PUBLISHING, PUBLISHED, FAILED, CLOSING, CLOSED, MERGED, ARCHIVED

### Changeset

| Field | Type | Description |
|-------|------|-------------|
| id | string (cs_...) | Unique identifier |
| changeset_spec_id | string | FK to ChangesetSpec (unique) |
| code_host_id | string | FK to CodeHost |
| external_id | string? | PR/MR number on code host |
| external_url | string? | URL to PR/MR on code host |
| branch_ref | string | Branch name on code host |
| is_draft | boolean | Whether published as draft |
| state | enum (OPEN, CLOSED, MERGED) | Current code host state |
| review_state | enum (PENDING, APPROVED, CHANGES_REQUESTED) | Review status |
| check_state | enum (PENDING, PASSED, FAILED) | CI check status |
| published_at | datetime? | Publication timestamp |
| merged_at | datetime? | Merge timestamp |
| closed_at | datetime? | Close timestamp |
| last_synced_at | datetime | Last sync from code host |

**Constraints**: Unique per changeset_spec_id. Unique per (code_host_id, external_id) when external_id is set.

### ChangesetEvent

| Field | Type | Description |
|-------|------|-------------|
| id | string (cse_...) | Unique identifier |
| changeset_id | string | FK to Changeset |
| event_type | enum (STATE_CHANGED, CI_STATUS_CHANGED, REVIEW_STATUS_CHANGED, MERGED, CLOSED, REOPENED) | Event type |
| payload | object | Event-specific data (old/new values) |
| occurred_at | datetime | Event timestamp |

### AuditEvent

| Field | Type | Description |
|-------|------|-------------|
| id | string (ae_...) | Unique identifier |
| actor_user_id | string | FK to User |
| namespace_id | string | FK to Namespace |
| resource_type | string | Type of resource affected |
| resource_id | string | ID of resource affected |
| action | string | Action performed |
| payload | object | Action-specific details |
| created_at | datetime | Event timestamp |

## Read Models (Projections)

### BatchChangeStats

| Field | Type | Description |
|-------|------|-------------|
| id | string (bc_...) | Matches BatchChange ID |
| total_workspaces | integer | Total workspace count |
| successful_specs | integer | Successful changeset spec count |
| failed_workspaces | integer | Failed execution count |
| unpublished_count | integer | Unpublished changesets |
| open_count | integer | Open changesets |
| merged_count | integer | Merged changesets |
| closed_count | integer | Closed changesets |
| ci_passed_count | integer | CI-passed changesets |
| ci_failed_count | integer | CI-failed changesets |
| review_approved_count | integer | Approved changesets |
| estimated_hours_saved | float | Computed hours saved |
| last_recomputed_at | datetime | Last projection update |

### BatchChangeBurndownDaily

| Field | Type | Description |
|-------|------|-------------|
| id | string (bc_...:YYYY-MM-DD) | Composite key |
| batch_change_id | string | FK to BatchChange |
| date | date | Calendar date |
| merged_count | integer | Merged as of date |
| open_count | integer | Open as of date |
| remaining_count | integer | Remaining as of date |

## State Machines

### BatchChange Lifecycle

```
DRAFT → PREVIEW_RUNNING → PREVIEW_READY → APPLYING → ACTIVE
  │                              │                      │
  │                              └──── (re-run) ────────┤
  │                                                     │
  └──────────────────────────── FAILED                  ├── PAUSED
                                                        └── ARCHIVED
```

### ChangesetSpec Lifecycle

```
UNPUBLISHED → PUBLISHING → PUBLISHED → MERGED
                  │             │
                  └── FAILED    ├── CLOSING → CLOSED
                                └── ARCHIVED
```

### WorkspaceExecution Lifecycle

```
QUEUED → RUNNING → SUCCEEDED
            │
            ├── FAILED
            └── CANCELLED

SKIPPED (excluded before execution)
```

## Index Strategy

See HLD Section 12 for the full compound index plan. Key indexes:

- `batch_changes`: `{ namespace_id: 1, updated_at: -1 }`
- `changeset_specs`: `{ batch_change_id: 1, repository_id: 1, workspace_path: 1 }`
- `changesets`: `{ code_host_id: 1, external_id: 1 }` (unique sparse)
- `changesets`: `{ batch_change_id: 1, state: 1, review_state: 1, check_state: 1 }`
- `changeset_events`: `{ changeset_id: 1, occurred_at: -1 }`
- `workspace_executions`: `{ batch_run_id: 1, state: 1 }`

## Concurrency Control

- Every mutable aggregate includes a `version` field for optimistic concurrency.
- State transitions use conditional updates: `update where _id = X AND version = Y`.
- Projections (stats, burndown) are rebuilt idempotently from primary documents + events.
