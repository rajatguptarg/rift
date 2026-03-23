# ADR-002: Temporal for Workflow Orchestration

**Date:** 2024-01-15  
**Status:** Accepted  
**Deciders:** Platform Engineering

---

## Context

Executing a batch spec against potentially thousands of repositories is a long-running, fault-tolerant distributed operation. Each workspace execution must: clone the repo, run N steps, capture the diff, and report back — independently. Failures in individual workspaces must not abort the entire run.

Candidate approaches: bare asyncio tasks, Celery, Apache Airflow, Temporal.

---

## Decision

We use **Temporal** (self-hosted, version 1.24) for orchestrating preview and apply workflows.

---

## Rationale

**Fan-out/fan-in pattern** maps naturally to Temporal child workflows or parallel activities:

```
PreviewWorkflow
  └─ for each repo:
       ├─ clone_repository (Activity)
       ├─ execute_steps (Activity)
       └─ capture_diff (Activity)
  └─ fan-in: aggregate results
```

| Criterion | Celery | Temporal |
|---|---|---|
| Durable execution | No (requires external state) | Native (event-sourced history) |
| Long-running workflows (hours) | Problematic with broker TTL | First-class support |
| Cancellation & signals | Manual | Built-in workflow signals |
| Visibility | Flower (limited) | Temporal UI (full history) |
| Python SDK quality | Mature | `temporalio` v1.x — production-ready |

Temporal's event-sourced history means any workflow or activity failure is automatically retried with back-off, and the workflow resumes from the last committed point — avoiding re-work on partial failures.

---

## Consequences

- **Positive**: Durable fan-out/fan-in; automatic retries; first-class cancellation; full execution history in Temporal UI.
- **Negative**: Additional operational dependency (Temporal cluster + Cassandra/PostgreSQL backend).
- **Mitigation**: Temporal is included in the `docker-compose.yml` dev setup; for production, the Helm chart provisions a separate Temporal deployment.
