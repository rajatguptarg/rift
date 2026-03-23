# ADR-003: REST + Server-Sent Events API Style

**Date:** 2024-01-15  
**Status:** Accepted  
**Deciders:** Platform Engineering

---

## Context

The Rift API must serve:

1. Standard CRUD for resources (batch changes, changesets, credentials, templates)
2. Real-time execution progress for the ExecutionView page — workspace states change continuously during a preview run

Candidate approaches: REST-only with polling, GraphQL subscriptions, WebSockets, REST + SSE.

---

## Decision

We use **REST (JSON over HTTP)** for all CRUD operations and **Server-Sent Events (SSE)** for streaming execution progress.

---

## Rationale

**REST** is chosen for CRUD because:
- Clear resource semantics (`GET /batch-changes/{id}`, `POST /batch-changes/{id}/preview`)
- Compatible with OpenAPI/Swagger codegen
- Straightforward HTTP caching and auth via Bearer tokens
- Aligns with existing Sourcegraph Batch Changes API contracts

**SSE** is chosen for streaming over WebSockets because:
- Unidirectional (server → client) — execution progress only flows one way
- Works over standard HTTP/1.1 — no upgrade handshake
- Natively supported by browser `EventSource` API
- Simpler than WebSockets for this use-case; no keepalive complexity
- FastAPI `StreamingResponse` with `text/event-stream` content-type works without additional libraries

The SSE endpoint (`GET /batch-changes/{id}/runs/{runId}/stream`) polls MongoDB every second and emits workspace execution state changes as JSON events. The frontend `useExecutionStream` hook updates the TanStack Query cache directly, providing a reactive UI without a full cache invalidation.

---

## Consequences

- **Positive**: Simpler than WebSockets; compatible with all modern browsers; no additional protocol support needed in load balancers.
- **Negative**: SSE connections are long-lived — requires async workers (uvicorn with multiple workers) to avoid connection exhaustion. HTTP/2 multiplexing is recommended for production.
- **Mitigation**: Connections have a maximum duration (10 minutes) after which the client must reconnect. The `EventSource` API auto-reconnects on network errors.
