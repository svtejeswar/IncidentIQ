# INC-2025-002 — Payment Service Database Connection Exhaustion

| Field | Value |
|---|---|
| **Incident ID** | INC-2025-002 |
| **Date** | 2025-04-02 |
| **Severity** | SEV1 |
| **Duration** | 1 hour 23 minutes |
| **Status** | Resolved |
| **Incident Commander** | Arjun Mehta |
| **Affected Services** | payment-service, checkout-service, postgres-primary, pgbouncer |
| **Document Type** | rca |

---

## Executive Summary

On April 2, 2025, the payment service experienced cascading failures stemming from PostgreSQL connection pool exhaustion on the primary database node. The incident began at 09:41 UTC and was fully resolved at 11:04 UTC. All payment processing, refund operations, and checkout flows were unavailable for the duration. Root cause was a connection leak introduced in a code deployment at 09:30 UTC: error handling in the transaction rollback path failed to close database connections under specific race conditions, causing connections to accumulate until the pool (max 100 connections via PgBouncer) was fully saturated. Approximately 8,400 payment transactions failed during the incident window.

---

## Timeline

| Time (UTC) | Event |
|---|---|
| 09:30 | Deployment of `payment-service v3.8.2` completed |
| 09:41 | PagerDuty alert: `payment_service_5xx_rate > 2%` |
| 09:44 | Alert escalated to SEV1: checkout failures confirmed via smoke tests |
| 09:48 | Incident Commander engaged, war room opened |
| 09:53 | Initial triage: PostgreSQL primary CPU normal, queries slow |
| 10:01 | PgBouncer dashboard shows 100/100 connections occupied, new connections queuing |
| 10:06 | Correlation with v3.8.2 deployment timeline confirmed |
| 10:11 | Code diff review identifies connection leak in `rollback_transaction()` error path |
| 10:18 | Decision: roll back to v3.8.1 rather than hotfix |
| 10:25 | Rollback deployed |
| 10:32 | PgBouncer connections begin releasing (leaked connections timeout at 30s) |
| 10:55 | Connection count normalizes, error rate drops below 0.5% |
| 11:04 | Incident resolved, post-mortem scheduled |

---

## Root Cause

**Primary:** A connection leak was introduced in `payment-service v3.8.2` within the `rollback_transaction()` function. The specific code path:

```python
async def rollback_transaction(conn, tx):
    try:
        await tx.rollback()
    except asyncpg.PostgresError as e:
        logger.error("Rollback failed", error=str(e))
        raise PaymentTransactionError(str(e))
        # BUG: conn.close() never called when rollback raises
    finally:
        pass  # Incorrectly replaced conn.release() during refactor
```

Under normal conditions, the `finally` block previously contained `await conn.release()`. During a code refactor to improve error messaging, `conn.release()` was accidentally removed and replaced with `pass`. This leak only triggered when a PostgreSQL error occurred during rollback — a path exercised frequently under production load but never reached in the test environment (test transactions succeeded, masking the bug).

**Contributing Factors:**

1. Test coverage for the transaction rollback failure path was absent.
2. The PR diff was large (312 lines) and the `finally: pass` change was visually unobtrusive.
3. PgBouncer max connections (100) was sized for normal load; no headroom for connection accumulation.
4. Connection leak detection alert did not exist.

---

## Resolution

1. Identified connection leak via PgBouncer monitoring dashboard.
2. Correlated leak start time with v3.8.2 deployment.
3. Reviewed code diff, located missing `conn.release()` in rollback path.
4. Rolled back to v3.8.1.
5. Waited for leaked connections to timeout and release (30-second timeout per connection).
6. Monitored PgBouncer connection count and payment error rate for 30 minutes post-recovery.
7. Manually re-queued 412 failed payment transactions from dead-letter queue.

---

## Customer Impact

- **8,400 payment transactions failed** during the 83-minute window.
- **2,100 checkout sessions** abandoned due to payment unavailability.
- Subscription renewals for **390 accounts** failed and required manual retry.
- Customer support volume increased 8× during the incident.
- Estimated revenue at risk: $340,000 in failed transaction value.
- Three enterprise customers triggered SLA breach notifications.

---

## Preventive Actions

| Action | Owner | Due Date | Status |
|---|---|---|---|
| Add unit tests for all database connection error paths, including rollback failure | Payments Team | 2025-04-16 | Complete |
| Add static analysis lint rule: flag any async db function with no `finally: release/close` | Platform Team | 2025-04-10 | Complete |
| Add PgBouncer connection saturation alert at 80% threshold | SRE Team | 2025-04-07 | Complete |
| Increase PgBouncer max connections to 200 for payment-service | DBA Team | 2025-04-09 | Complete |
| Require two senior reviewers for payment-service PRs touching transaction handling | Payments Lead | 2025-04-05 | Complete |
| Implement connection leak detection via periodic pool audit daemon | Platform Team | 2025-05-01 | In Progress |
| Add retry logic to checkout for transient payment failures | Checkout Team | 2025-05-15 | Planned |

---

## Related Runbooks

- [RUN-PAY-001: Payment Service Recovery Under Database Failure](../runbooks/RUN-PAY-001.md)
- [RUN-PG-001: PostgreSQL Connection Pool Exhaustion](../runbooks/RUN-PG-001.md)
- [RUN-PG-002: PgBouncer Emergency Configuration](../runbooks/RUN-PG-002.md)

---

## Lessons Learned

- Connection management in async Python requires explicit `finally` blocks — async context managers (async with) should be preferred to make closure automatic and unambiguous.
- Large PRs touching critical infrastructure should be broken into smaller, independently reviewable units. A 312-line diff obscures a 1-line regression.
- Test coverage for error/exception paths in transaction handling is not optional — happy-path tests cannot validate failure recovery.
- Connection pool exhaustion and Redis pool exhaustion follow identical failure signatures: silent accumulation until saturation, then hard failure. Both require low-threshold utilization alerts, not just error-rate alerts.
