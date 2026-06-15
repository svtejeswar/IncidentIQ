# IncidentIQ — API Design

Base URL: `/api/v1`

All responses follow the envelope pattern:
```json
{
  "success": true,
  "data": { ... },
  "error": null,
  "meta": { "request_id": "...", "timestamp": "..." }
}
```

---

## Documents

### POST /documents/upload

Upload an operational document for processing.

**Request** — `multipart/form-data`

| Field | Type | Required | Description |
|---|---|---|---|
| `file` | File | Yes | PDF, DOCX, TXT, or MD |
| `document_type` | string | Yes | `incident_report` \| `rca` \| `runbook` \| `postmortem` \| `architecture` \| `troubleshooting_guide` |
| `title` | string | No | Defaults to filename |

**Response 202 Accepted**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Payment Service Outage - March 2024",
  "document_type": "incident_report",
  "filename": "payment-outage-march-2024.pdf",
  "status": "pending",
  "created_at": "2024-03-15T14:32:00Z",
  "stream_url": "/api/v1/documents/550e8400.../stream"
}
```

---

### GET /documents/{id}/stream

Server-Sent Events stream for real-time processing updates.

**Response** — `text/event-stream`

```
data: {"stage": "uploading", "message": "Saving file...", "progress": 10}

data: {"stage": "extracting", "message": "Extracting text from PDF...", "progress": 25}

data: {"stage": "chunking", "message": "Splitting into 47 chunks...", "progress": 45}

data: {"stage": "enriching", "message": "Extracting metadata...", "progress": 60}

data: {"stage": "embedding", "message": "Generating embeddings...", "progress": 80}

data: {"stage": "indexing", "message": "Storing in vector index...", "progress": 95}

data: {"stage": "completed", "message": "Ready. 47 chunks indexed.", "progress": 100, "chunk_count": 47}
```

**Error event:**
```
data: {"stage": "failed", "message": "Failed to extract text: corrupted PDF", "progress": 0}
```

---

### GET /documents

List all documents.

**Query Parameters**

| Param | Type | Default | Description |
|---|---|---|---|
| `skip` | int | 0 | Pagination offset |
| `limit` | int | 20 | Max results (max 100) |
| `status` | string | null | Filter by status |
| `document_type` | string | null | Filter by type |

**Response 200**
```json
{
  "items": [
    {
      "id": "550e8400-...",
      "title": "Payment Service Outage",
      "document_type": "incident_report",
      "status": "completed",
      "chunk_count": 47,
      "created_at": "2024-03-15T14:32:00Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 20
}
```

---

### GET /documents/{id}

Get a specific document by ID.

**Response 200** — Full DocumentResponse

**Response 404**
```json
{"detail": "Document not found"}
```

---

### DELETE /documents/{id}

Delete a document and all its chunks.

**Response 204 No Content**

---

## Search

### POST /search

Semantic search across all indexed knowledge.

**Request Body**
```json
{
  "query": "database connection timeouts in payment service",
  "limit": 5,
  "document_types": ["incident_report", "rca"],
  "include_ai_answer": true
}
```

| Field | Type | Default | Description |
|---|---|---|---|
| `query` | string | required | Natural language query |
| `limit` | int | 5 | Number of results (max 20) |
| `document_types` | string[] | null | Filter by document types |
| `include_ai_answer` | bool | true | Generate AI answer from results |

**Response 200**
```json
{
  "query": "database connection timeouts in payment service",
  "ai_answer": "Based on 3 historical incidents, connection timeouts in the payment service were primarily caused by connection pool exhaustion under high load...",
  "results": [
    {
      "document_id": "550e8400-...",
      "title": "Payment DB Timeout - Jan 2024",
      "document_type": "incident_report",
      "relevance_score": 0.92,
      "excerpt": "...connection pool was exhausted after a surge in checkout traffic...",
      "root_cause": "Connection pool size set too low (max_connections=10)",
      "resolution": "Increased max_connections to 100, added connection pooling middleware",
      "affected_services": ["payment-service", "postgres-primary"],
      "severity": "critical"
    }
  ],
  "total_results": 3,
  "search_latency_ms": 342
}
```

---

### POST /search/similar

Find incidents similar to a given document or text snippet.

**Request Body**
```json
{
  "document_id": "550e8400-...",
  "limit": 5
}
```

OR

```json
{
  "text": "Users cannot complete checkout. Payment service returning 503.",
  "limit": 5
}
```

**Response 200**
```json
{
  "similar_incidents": [
    {
      "document_id": "...",
      "title": "Checkout Failure - Dec 2023",
      "similarity_score": 0.87,
      "shared_root_causes": ["connection_pool_exhaustion"],
      "shared_services": ["payment-service"],
      "resolution_summary": "Scaled connection pool + added circuit breaker"
    }
  ]
}
```

---

## AI Assistant

### POST /assistant/chat

Ask a natural language question about operational knowledge.

**Request Body**
```json
{
  "message": "Have we seen login service failures before? What caused them?",
  "conversation_id": "conv_abc123",
  "history": [
    {"role": "user", "content": "What services commonly fail together?"},
    {"role": "assistant", "content": "Based on our incident history..."}
  ]
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `message` | string | Yes | User's question |
| `conversation_id` | string | No | For multi-turn context |
| `history` | Message[] | No | Prior conversation turns |

**Response 200**
```json
{
  "conversation_id": "conv_abc123",
  "answer": "Yes, we've had 4 login service incidents. The most common cause was...",
  "sources": [
    {
      "document_id": "...",
      "title": "Login Service Outage - Feb 2024",
      "excerpt": "...authentication token validation was failing due to...",
      "relevance_score": 0.94
    }
  ],
  "suggested_runbooks": [
    {
      "document_id": "...",
      "title": "Login Service Recovery Runbook",
      "relevance_score": 0.88
    }
  ]
}
```

---

## Health

### GET /health

Liveness check.

**Response 200**
```json
{"status": "ok", "version": "1.0.0"}
```

### GET /health/ready

Readiness check — verifies MongoDB connectivity.

**Response 200**
```json
{
  "status": "ready",
  "checks": {
    "mongodb": "ok",
    "embeddings": "ok"
  }
}
```

**Response 503** — if any check fails.

---

## Error Codes

| HTTP Status | Code | Description |
|---|---|---|
| 400 | `VALIDATION_ERROR` | Invalid request body or params |
| 404 | `NOT_FOUND` | Resource does not exist |
| 413 | `FILE_TOO_LARGE` | File exceeds 50MB limit |
| 415 | `UNSUPPORTED_FILE_TYPE` | Only PDF, DOCX, TXT, MD allowed |
| 422 | `UNPROCESSABLE` | File content cannot be extracted |
| 500 | `INTERNAL_ERROR` | Unexpected server error |
| 503 | `SERVICE_UNAVAILABLE` | Dependency (MongoDB/Groq) unavailable |
