# Core Lifecycle Sanity Check: Rift Batch Changes Platform

**Purpose**: Lightweight self-review validating requirement quality for the core lifecycle flows (create → preview → apply → publish → track)
**Created**: 2026-03-23
**Feature**: [spec.md](../spec.md)
**Depth**: Sanity Check
**Audience**: Spec author (self-review)
**Focus**: US1 (Create/Execute), US2 (Publish/Track), FR-001–FR-017, state machines

## Requirement Completeness

- [ ] CHK001 - Are all BatchChange state transitions (DRAFT → PREVIEW_RUNNING → PREVIEW_READY → APPLYING → ACTIVE → PAUSED → ARCHIVED) explicitly described with trigger conditions and guards? [Completeness, Spec §data-model State Machines]
- [ ] CHK002 - Are requirements defined for the FAILED state — including which errors cause it and whether the user can retry from FAILED? [Gap]
- [ ] CHK003 - Is the transition from ACTIVE back to PREVIEW_RUNNING (re-run after spec edit) fully specified, including what happens to existing changesets? [Completeness, Spec §Edge Case 7]
- [ ] CHK004 - Are requirements for the PAUSED state documented — who can pause, what pausing stops, and how to resume? [Gap]
- [ ] CHK005 - Is the batch spec YAML schema (name, description, on, steps, changesetTemplate, workspaces) formally specified or referenced? [Completeness, Spec §FR-001]

## Requirement Clarity

- [ ] CHK006 - Is "near-real-time" for changeset status updates quantified with a specific latency target? [Clarity, Spec §FR-011]
- [ ] CHK007 - Is "isolated containers" defined with specific isolation requirements (non-root, no Docker socket, egress rules)? [Clarity, Spec §FR-003]
- [ ] CHK008 - Is "real-time per-workspace logs" in the execution screen defined — streaming vs polling, latency, log retention? [Clarity, Spec §US1 Scenario 3]
- [ ] CHK009 - Is the search query syntax for the `on` field (repository matching) specified or referenced? [Clarity, Spec §FR-002]
- [ ] CHK010 - Is "bulk actions" scope defined — maximum selection size, timeout, partial failure handling? [Clarity, Spec §FR-010]

## Scenario Coverage

- [ ] CHK011 - Are requirements defined for what happens when a user cancels an in-progress preview execution? [Coverage, Gap]
- [ ] CHK012 - Are requirements defined for concurrent spec edits — what happens if two users edit the same batch change simultaneously? [Coverage, Gap]
- [ ] CHK013 - Are requirements specified for re-applying a batch change when some changesets are already merged on the code host? [Coverage, Gap]
- [ ] CHK014 - Are requirements for partial execution success defined — e.g., 150 of 200 workspaces succeed, user wants to apply only the successful ones? [Coverage, Spec §FR-026]
- [ ] CHK015 - Is the publish workflow specified for code hosts that don't support draft PRs (e.g., Bitbucket Server)? [Coverage, Spec §FR-009]

## Edge Case Coverage

- [ ] CHK016 - Are recovery requirements defined when a workspace execution times out mid-run? [Edge Case, Gap]
- [ ] CHK017 - Are requirements specified for what happens when a code host is unreachable during the publish step? [Edge Case, Spec §FR-009]
- [ ] CHK018 - Is the behavior defined when the reconciliation loop detects a changeset was force-closed or deleted externally? [Edge Case, Spec §FR-017]
- [ ] CHK019 - Are rate limit handling requirements specific enough — backoff algorithm, max retries, user notification? [Edge Case, Spec §Edge Case 2]
- [ ] CHK020 - Is the conflict detection for overlapping batch changes specified beyond "warn the user" — does it block, allow override, or require resolution? [Edge Case, Spec §FR-027]

## Acceptance Criteria Quality

- [ ] CHK021 - Can SC-001 ("under 10 minutes for up to 100 repositories") be objectively measured — is the start and end point of the timer defined? [Measurability, Spec §SC-001]
- [ ] CHK022 - Is SC-003 ("within 60 seconds") measurable end-to-end — from code host webhook receipt to dashboard UI update? [Measurability, Spec §SC-003]
- [ ] CHK023 - Is SC-006 ("complete visibility… no need to visit code host UIs") measurable or only a subjective user survey metric? [Measurability, Spec §SC-006]

## State Machine Consistency

- [ ] CHK024 - Do the ChangesetSpec lifecycle states (UNPUBLISHED → PUBLISHING → PUBLISHED → MERGED / CLOSED / ARCHIVED) map consistently to the three publish modes in FR-009 (full, draft, push-only)? [Consistency, Spec §FR-009 ↔ data-model]
- [ ] CHK025 - Is the relationship between WorkspaceExecution SUCCEEDED state and ChangesetSpec creation documented — does every SUCCEEDED execution produce exactly one ChangesetSpec? [Consistency, Gap]
- [ ] CHK026 - Are the conditions under which a Changeset moves to CLOSED vs ARCHIVED consistent between the reconciliation loop and manual bulk actions? [Consistency, Spec §FR-010 ↔ FR-017]

## Notes

- This is a lightweight sanity check focused on the core create/preview/apply/publish/track lifecycle before task generation.
- Items reference spec.md (FR-001–FR-017, US1, US2, edge cases) and data-model.md (state machines).
- Address gaps before proceeding to `/speckit.tasks`.
