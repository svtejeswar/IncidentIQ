# ADR-003: Server-Sent Events for Real-Time Processing Updates

**Status:** Accepted
**Date:** 2024-01-01

## Context

Document processing (extract → chunk → embed → index) takes 5–30 seconds depending on file size. Users need feedback on progress. Options: polling, WebSockets, SSE.

## Decision

Use Server-Sent Events (SSE) via `GET /api/v1/documents/{id}/stream`.

Processing stages emit typed events:
```
uploading → extracting → chunking → enriching → embedding → indexing → completed
```

Each event carries: `stage`, `message`, `progress (0-100)`, and optional `chunk_count`.

## Rationale

| Option | Reason for/against |
|---|---|
| Polling | Simple but wastes requests, adds latency |
| WebSockets | Bidirectional overhead not needed here; harder to proxy |
| SSE | Unidirectional, HTTP/1.1 compatible, native browser support, simple to implement in FastAPI |

SSE is the right fit for one-way server-to-client streaming of progress events.

## Consequences

**Positive:**
- Simple `EventSource` API on frontend — no library needed
- Works through standard HTTP proxies and load balancers
- FastAPI's `StreamingResponse` with `text/event-stream` is straightforward

**Negative:**
- Limited to one connection per document per browser tab
- No built-in reconnection for missed events (acceptable for this use case)

## Implementation

Backend: `StreamingResponse` with an async generator that yields `data: {json}\n\n`
Frontend: `useSSE` hook wrapping `new EventSource(url)` with cleanup on unmount
