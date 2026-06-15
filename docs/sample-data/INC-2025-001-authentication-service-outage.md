# INC-2025-001 — Authentication Service Outage

| Field | Value |
|---|---|
| **Incident ID** | INC-2025-001 |
| **Date** | 2025-03-14 |
| **Severity** | SEV1 |
| **Duration** | 47 minutes |
| **Status** | Resolved |
| **Incident Commander** | Priya Nair |
| **Affected Services** | auth-service, api-gateway, redis-auth-cluster |
| **Document Type** | postmortem |

---

## Executive Summary

On March 14, 2025, the authentication service experienced a complete outage lasting 47 minutes between 14:23 UTC and 15:10 UTC. All user login, token refresh, and session validation requests failed with HTTP 503 errors. The root cause was Redis connection pool exhaustion — a recent configuration change had reduced the maximum connection pool size from 500 to 50, which was insufficient to handle peak traffic. Approximately 23,000 users were unable to log in or maintain authenticated sessions during the incident window.

---

## Timeline

| Time (UTC) | Event |
|---|---|
| 14:23 | PagerDuty alert fires: `auth_service_error_rate > 5%` |
| 14:26 | On-call engineer (Priya Nair) acknowledges alert |
| 14:29 | Initial investigation: auth-service pods healthy, Redis cluster healthy |
| 14:35 | Redis connection pool metrics inspected — pool exhausted at 50/50 connections |
| 14:40 | Config change identified: `REDIS_MAX_CONNECTIONS` reduced from 500 to 50 in a Helm values update deployed at 14:15 |
| 14:45 | Rollback initiated to previous Helm chart revision |
| 14:52 | Rollback completed, Redis pool connections recovering |
| 15:05 | Error rate drops below 0.1% |
| 15:10 | Incident resolved, all-clear issued |
| 15:30 | Post-incident review meeting scheduled |

---

## Root Cause

**Primary:** The `REDIS_MAX_CONNECTIONS` environment variable was inadvertently changed from `500` to `50` in a Helm values file update. This change was introduced in PR #1847 as part of a resource optimization effort targeting non-critical services. The authentication service was incorrectly included in the batch update.

**Contributing Factors:**

1. The Helm values file applied a global `redis.maxConnections: 50` override that was not service-specific, affecting all services sharing the config template.
2. No load testing was performed after the configuration change.
3. Alerting on Redis connection pool utilization existed but the threshold was set to 95%, which was only reached after the service was already failing.
4. The config change was reviewed as a "minor infrastructure tweak" and did not go through the standard change review process for auth-service modifications.

---

## Resolution

1. Identified the misconfigured `REDIS_MAX_CONNECTIONS` value via Redis metrics dashboard.
2. Rolled back Helm release to revision `auth-service-v2.14.1` (previous stable).
3. Monitored error rates and connection pool recovery for 15 minutes post-rollback.
4. Issued all-clear once error rate stabilized below 0.1% for 5 consecutive minutes.

---

## Customer Impact

- **23,000+ users** unable to authenticate during the 47-minute outage window.
- **4,200 active sessions** invalidated mid-flow due to token refresh failures.
- Customer support received **312 tickets** during the incident window.
- SLA breach for three enterprise customers (99.9% monthly uptime commitment).
- Estimated revenue impact: $18,000 in chargebacks and SLA credits.

---

## Preventive Actions

| Action | Owner | Due Date | Status |
|---|---|---|---|
| Add auth-service to change freeze list requiring explicit approval | Platform Team | 2025-03-21 | Complete |
| Lower Redis connection pool alert threshold from 95% to 70% | SRE Team | 2025-03-18 | Complete |
| Create service-specific Helm values files — eliminate global overrides | Platform Team | 2025-03-28 | In Progress |
| Add integration test: Redis pool under peak load simulation | Auth Team | 2025-04-01 | Planned |
| Implement circuit breaker on auth-service → Redis path | Auth Team | 2025-04-15 | Planned |
| Add Redis pool exhaustion to runbook and training material | SRE Team | 2025-03-25 | Complete |

---

## Related Runbooks

- [RUN-AUTH-001: Authentication Service Recovery Procedure](../runbooks/RUN-AUTH-001.md)
- [RUN-REDIS-002: Redis Connection Pool Exhaustion](../runbooks/RUN-REDIS-002.md)
- [RUN-HELM-003: Helm Chart Rollback Procedure](../runbooks/RUN-HELM-003.md)

---

## Lessons Learned

- Configuration changes to critical infrastructure services (auth, payments) must always go through the full change review process regardless of perceived scope.
- Global configuration templates create hidden blast radius — a "minor tweak" can silently reconfigure unrelated critical services.
- Alert thresholds should be set proactively at 70% of known failure points, not reactively at 95%.
- Redis connection pool exhaustion is a silent failure mode — the connection pool fills up before error rates spike, meaning by the time alerts fire the service is already degraded.
