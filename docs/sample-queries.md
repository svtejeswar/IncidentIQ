# IncidentIQ — Sample Query Guide

Use these queries in the **Search** or **AI Assistant** interface after uploading the documents from `docs/sample-data/`.

---

## A. Basic Retrieval

### A1. What caused the authentication outage?

**Expected documents retrieved:** INC-2025-001

**Example AI answer:**
> The authentication service outage on March 14, 2025 was caused by Redis connection pool exhaustion. A Helm chart update reduced `REDIS_MAX_CONNECTIONS` from 500 to 50, which was insufficient to handle peak traffic. The configuration change was applied globally across services and inadvertently included the auth service, which was not the intended target.

---

### A2. Which services were affected during the payment failure?

**Expected documents retrieved:** INC-2025-002

**Example AI answer:**
> The payment service incident on April 2, 2025 affected: `payment-service`, `checkout-service`, `postgres-primary`, and `pgbouncer`. The checkout service was unable to complete transactions while the payment service was unavailable.

---

### A3. What was the customer impact of the Redis cache failure?

**Expected documents retrieved:** INC-2025-003

**Example AI answer:**
> During the Redis cache failure on April 19, 2025, approximately 41,000 user sessions were affected. Product catalog pages showed partial data or failed to load, recommendation sections were completely unavailable, and search latency increased by 8×. The estimated revenue impact was $76,000 in lost conversion.

---

### A4. What triggered the SQS message backlog incident?

**Expected documents retrieved:** INC-2025-004

**Example AI answer:**
> An IAM permission misconfiguration removed `sqs:ReceiveMessage` from the Lambda execution role during a routine IAM role rotation. Without this permission, the Lambda consumer silently stopped polling the SQS queue. Over 3 hours and 42 minutes, 28,400 order messages accumulated in the queue with no processing occurring.

---

### A5. What caused the API Gateway latency spike?

**Expected documents retrieved:** INC-2025-005

**Example AI answer:**
> An N+1 query pattern was introduced in `product-service v4.1.0`. The new enriched product detail endpoint made a separate call to the inventory service and pricing service for each product variant. For a product with 47 variants, this generated 94 downstream service calls per request. Under production load, this caused the downstream services to become saturated, resulting in p99 API Gateway latency exceeding 9 seconds.

---

## B. Resolution Queries

### B1. How was the authentication service outage resolved?

**Expected documents retrieved:** INC-2025-001

**Example AI answer:**
> The authentication outage was resolved by rolling back the Helm release to the previous revision (`auth-service-v2.14.1`), which restored the original `REDIS_MAX_CONNECTIONS` value of 500. After rollback, Redis connection pool recovery was monitored for 15 minutes until the error rate dropped below 0.1%.

---

### B2. What preventive actions were recommended after the payment database incident?

**Expected documents retrieved:** INC-2025-002

**Example AI answer:**
> Key preventive actions included: (1) adding unit tests for all database connection error paths including rollback failure scenarios, (2) adding a static analysis lint rule to flag async database functions missing `finally: release/close`, (3) adding a PgBouncer connection saturation alert at 80% threshold, (4) increasing PgBouncer max connections to 200 for the payment service, and (5) requiring two senior reviewers for payment-service PRs touching transaction handling.

---

### B3. How was the Kubernetes pod crash loop fixed?

**Expected documents retrieved:** INC-2025-006

**Example AI answer:**
> The crash loop was caused by a Jinja2 template environment memory leak. The fix replaced the global `Environment()` singleton (which cached all compiled templates indefinitely) with a per-render instantiation using `cache_size=0`. The emergency mitigation of increasing the container memory limit from 512 MB to 1 GB was deployed first, but this only delayed the crash — the root cause fix was required to stop the memory growth.

---

### B4. What was the resolution time for the SQS incident and how was the backlog cleared?

**Expected documents retrieved:** INC-2025-004

**Example AI answer:**
> The IAM permission was restored at 09:47 UTC, approximately 3 hours and 32 minutes after the initial misconfiguration. Lambda resumed polling immediately upon permission restoration. The 28,400-message backlog was fully drained by 14:30 UTC. The 412 payment transactions that had failed before the backlog drain were manually re-queued from the dead-letter queue.

---

## C. Cross-Incident Discovery

### C1. Show incidents related to connection leaks or connection pool exhaustion

**Expected documents retrieved:** INC-2025-001, INC-2025-002

**Example AI answer:**
> Two incidents involved connection pool exhaustion:
> - **INC-2025-001**: Redis connection pool exhausted in the authentication service due to a misconfigured `REDIS_MAX_CONNECTIONS` value (reduced from 500 to 50).
> - **INC-2025-002**: PostgreSQL connection pool exhausted in the payment service due to a connection leak in the transaction rollback error path — connections were never released when a `PostgresError` occurred during rollback.
>
> Both incidents share the same failure signature: silent accumulation of connections until the pool is saturated, followed by hard failure.

---

### C2. Have we seen Redis-related failures before?

**Expected documents retrieved:** INC-2025-001, INC-2025-003

**Example AI answer:**
> Yes, two incidents involved Redis failures:
> - **INC-2025-001 (March 14)**: Redis connection pool exhausted in the auth service — a configuration change reduced the pool size below production requirements.
> - **INC-2025-003 (April 19)**: Redis primary node OOM-killed, triggering a cache stampede on PostgreSQL. Root cause was `maxmemory-policy: noeviction` combined with a data migration that exceeded memory limits.
>
> Both incidents point to Redis configuration management as a recurring risk area.

---

### C3. Find incidents involving resource exhaustion

**Expected documents retrieved:** INC-2025-001, INC-2025-002, INC-2025-003, INC-2025-006

**Example AI answer:**
> Four incidents involved resource exhaustion:
> - **INC-2025-001**: Redis connection pool exhausted (auth service) — misconfigured pool size.
> - **INC-2025-002**: PostgreSQL connection pool exhausted (payment service) — connection leak in rollback path.
> - **INC-2025-003**: Redis memory exhausted (cache cluster) — unbounded key growth with noeviction policy.
> - **INC-2025-006**: Container memory exhausted (notification service) — Jinja2 template cache memory leak.
>
> Resource exhaustion is the single most common failure category across our incident history.

---

### C4. Find incidents caused by configuration changes or misconfigurations

**Expected documents retrieved:** INC-2025-001, INC-2025-004

**Example AI answer:**
> Two incidents were directly caused by configuration or infrastructure misconfigurations:
> - **INC-2025-001**: A Helm values file global override reduced `REDIS_MAX_CONNECTIONS` for the auth service from 500 to 50 — a configuration change that bypassed the normal auth service change review process.
> - **INC-2025-004**: An IAM role rotation script used an incomplete policy template, removing `sqs:ReceiveMessage` from the Lambda execution role during a routine rotation cycle.

---

### C5. Which incidents were caused by code deployments?

**Expected documents retrieved:** INC-2025-002, INC-2025-005

**Example AI answer:**
> Two incidents were directly triggered by code deployments:
> - **INC-2025-002**: `payment-service v3.8.2` introduced a connection leak — `conn.release()` was accidentally removed from the transaction rollback `finally` block during a refactor.
> - **INC-2025-005**: `product-service v4.1.0` introduced an N+1 call pattern — the enriched product detail endpoint made individual downstream calls per product variant rather than batching them.

---

## D. Operational Intelligence

### D1. What recurring root causes appear across incidents?

**Expected documents retrieved:** INC-2025-001, INC-2025-002, INC-2025-003, INC-2025-004, INC-2025-005, INC-2025-006

**Example AI answer:**
> Analysis of all six incidents reveals three recurring root cause categories:
>
> **1. Resource exhaustion (4 incidents):**
> Redis connection pool (INC-001), PostgreSQL connection pool (INC-002), Redis memory (INC-003), container memory / Jinja2 leak (INC-006). Common pattern: a component fills up silently, then fails hard.
>
> **2. Missing or inadequate monitoring (all 6 incidents):**
> In every incident, the monitoring system failed to provide early warning. Alerts fired only after service degradation had begun — or not at all (INC-004 — Lambda silently stopped).
>
> **3. Insufficient pre-deployment testing (3 incidents):**
> INC-002 (no rollback failure path tests), INC-005 (no multi-variant load tests), INC-006 (load tests not long enough to detect slow memory leak).

---

### D2. Which incidents impacted customer transactions?

**Expected documents retrieved:** INC-2025-001, INC-2025-002, INC-2025-004, INC-2025-005

**Example AI answer:**
> Four incidents directly impacted customer-facing transactions:
> - **INC-2025-001**: 23,000 users unable to log in; 4,200 active sessions invalidated. Customers couldn't access the platform.
> - **INC-2025-002**: 8,400 payment transactions failed; 2,100 checkout sessions abandoned. Direct revenue impact of ~$340,000 in failed transaction value.
> - **INC-2025-004**: 28,400 order messages unprocessed; no order confirmations or fulfillment updates for ~4 hours.
> - **INC-2025-005**: Cart abandonment rate increased 34%; estimated $52,000 in abandoned cart revenue during the latency spike.

---

### D3. Which incidents involved database failures?

**Expected documents retrieved:** INC-2025-002, INC-2025-003

**Example AI answer:**
> Two incidents involved direct database failures:
> - **INC-2025-002**: PostgreSQL connection pool exhaustion caused all payment database operations to fail. PgBouncer max connections (100) saturated due to a connection leak in the payment service.
> - **INC-2025-003**: Redis cache failure caused a thundering herd of 14,000 queries/second to hit PostgreSQL, driving query latency from 8 ms to 4,200 ms and causing cascade failures in catalog, recommendation, and search services.

---

### D4. What monitoring gaps were identified across incidents?

**Expected documents retrieved:** INC-2025-001, INC-2025-002, INC-2025-003, INC-2025-004, INC-2025-006

**Example AI answer:**
> Monitoring gaps identified across incidents:
> - **Connection pool utilization alerts set too high** (INC-001, INC-002): thresholds at 95% mean alerts fire only after failure is already in progress. Recommended: 70–80%.
> - **No Redis memory growth alerting** (INC-003): memory only monitored post-OOM via `container_oom_kills`.
> - **No SQS queue depth alerting** (INC-004): Lambda stopping silently was undetected for 3+ hours. Age-of-oldest-message is the key metric.
> - **No memory growth rate alerting** (INC-006): container OOM kill was the only alert; a memory growth trend alert would have given 2+ hours of warning.

---

### D5. Which incidents had the longest resolution time and why?

**Expected documents retrieved:** INC-2025-004, INC-2025-006, INC-2025-003

**Example AI answer:**
> The three longest incidents:
> - **INC-2025-004 (3h 42m)**: SQS message backlog — Lambda stopped silently with no immediate error. Detection took 3+ hours because no queue depth alert existed.
> - **INC-2025-006 (4h 18m)**: Kubernetes crash loop — occurred at 02:17 UTC (overnight); limited on-call coverage; on-call applied memory limit increase (masking fix) rather than finding root cause, leading to a second OOM crash 2 hours later.
> - **INC-2025-003 (2h 11m)**: Redis cache stampede — root cause (Redis OOM) resolved quickly, but thundering herd recovery required manual cache warming before PostgreSQL latency normalized.

---

### D6. What are the most expensive incidents by customer impact?

**Expected documents retrieved:** INC-2025-002, INC-2025-005, INC-2025-003

**Example AI answer:**
> Ranked by estimated revenue impact:
> 1. **INC-2025-002** — Payment database exhaustion: $340,000 in failed transaction value; 8,400 payment failures; 3 enterprise SLA breaches.
> 2. **INC-2025-005** — API Gateway latency spike: $52,000 in abandoned cart revenue; 34% increase in cart abandonment.
> 3. **INC-2025-003** — Redis cache stampede: $76,000 in lost conversion; 41,000 affected user sessions.
