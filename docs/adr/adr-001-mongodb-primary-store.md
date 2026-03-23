# ADR-001: MongoDB as Primary Data Store

**Date:** 2024-01-15  
**Status:** Accepted  
**Deciders:** Platform Engineering

---

## Context

Rift Batch Changes stores several interconnected domain entities: batch changes, batch specs, batch runs, workspace executions, changesets, and audit events. These records have hierarchical relationships (batch change → batch run → workspace executions) and require:

- Flexible schema evolution (batch spec YAML structures vary by user input)
- Cursor-based pagination over large result sets
- Atomic document updates with optimistic concurrency control
- Aggregation for burndown/analytics queries

Candidate stores evaluated: PostgreSQL, MongoDB, CockroachDB.

---

## Decision

We use **MongoDB 7.0** as the primary operational data store, accessed via the **Motor** async driver.

---

## Rationale

| Criterion | PostgreSQL | MongoDB |
|---|---|---|
| Schema flexibility | Requires migrations for YAML blob columns | Native document model; no migration for spec YAML |
| Async Python driver | asyncpg (good) | Motor (first-class, well maintained) |
| Cursor pagination | Keyset pagination with indexes | `_id`-based cursor, natural fit |
| Aggregation | SQL `GROUP BY` | Aggregation Pipeline; cleaner for burndown |
| Horizontal scale | Requires Citus or partitioning | Native sharding |

Optimistic concurrency is implemented via a `version` integer field: `update_with_version(id, version, patch)` issues `{$set: patch, $inc: {version: 1}}` with the filter `{_id: id, version: version}` and raises `OptimisticLockError` if the matched count is zero.

---

## Consequences

- **Positive**: Flexible document model for batch spec YAML; simple cursor pagination; native async support via Motor.
- **Negative**: No JOIN semantics — service layer must perform multi-collection lookups manually.
- **Mitigation**: BaseRepository[T] generic provides consistent CRUD; compound indexes defined at startup prevent full-collection scans.
