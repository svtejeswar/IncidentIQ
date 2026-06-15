# INC-2025-006 — Kubernetes Pod Crash Loop Incident

| Field | Value |
|---|---|
| **Incident ID** | INC-2025-006 |
| **Date** | 2025-06-03 |
| **Severity** | SEV3 |
| **Duration** | 4 hours 18 minutes |
| **Status** | Resolved |
| **Incident Commander** | Marcus Lindqvist |
| **Affected Services** | notification-service, email-delivery-service, push-notification-gateway |
| **Document Type** | postmortem |

---

## Executive Summary

On June 3, 2025, the notification-service began entering a crash loop on all 6 Kubernetes pods starting at 02:17 UTC. The service was OOM-killed by the Kubernetes node (memory limit: 512 MB) and entered `CrashLoopBackOff` state, with exponential restart backoff causing notification delivery to be completely unavailable for 4 hours and 18 minutes until the incident was resolved at 06:35 UTC. The long resolution time was primarily due to the incident occurring outside business hours with limited on-call coverage. Root cause was a memory leak in the notification template rendering subsystem: a poorly managed Jinja2 template environment accumulated compiled template objects in memory indefinitely, growing at approximately 12 MB/hour under normal traffic until the 512 MB container limit was hit.

---

## Timeline

| Time (UTC) | Event |
|---|---|
| 02:17 | notification-service pod memory reaches 512 MB limit; OOM-kill by kubelet |
| 02:17 | Kubernetes restarts pods; CrashLoopBackOff begins |
| 02:17 | PagerDuty alert: `notification_service_pod_restarts > 3` |
| 02:19 | On-call acknowledges (low-severity overnight); observes CrashLoopBackOff |
| 02:22 | On-call determines root cause not immediately identifiable; escalation deferred |
| 02:22 | Runbook action: increase memory limit to 1 GB to restore service temporarily |
| 02:28 | Memory limit increased; pods restart successfully |
| 02:30 | Service restored but memory leak continues unresolved |
| 04:41 | Pods hit 1 GB limit; OOM-killed again; CrashLoopBackOff resumes |
| 05:15 | Engineering lead (Marcus Lindqvist) engaged |
| 05:25 | Memory growth profiling initiated via `kubectl exec` + py-spy |
| 05:48 | Memory leak identified in Jinja2 template environment cache |
| 06:05 | Hotfix deployed: template environment cleared per render cycle |
| 06:20 | Pods stabilize; memory growth stops |
| 06:35 | Incident resolved; all notifications processed from backlog |

---

## Root Cause

**Primary:** The notification-service Jinja2 template environment was instantiated as a global singleton (`Environment()`) with default settings. Jinja2 compiles each template it encounters and stores the compiled bytecode in an internal `_parse_cache`. Under the notification-service's workload — hundreds of distinct per-customer template variations loaded at runtime — this cache grew without bound.

```python
# notification-service — memory leak (before fix)
from jinja2 import Environment

_env = Environment()  # Global singleton — cache grows indefinitely

def render_notification(template_str: str, context: dict) -> str:
    template = _env.from_string(template_str)  # Cached forever
    return template.render(**context)
```

With 6,000+ unique template strings processed per day (custom notification templates per customer account), the compiled template cache accumulated approximately 12 MB/hour, reaching 512 MB after ~42 hours of operation.

**Contributing Factors:**

1. The Jinja2 `Environment` singleton was created in an early prototype phase and was never reviewed for production suitability.
2. Container memory limit (512 MB) was set based on peak observed usage during load testing — load testing did not run long enough to observe the memory leak trend.
3. No memory growth alerting existed — only `container_oom_kills` alert, which fires only after the crash.
4. On-call runbook escalation for CrashLoopBackOff defaulted to "increase memory limit" without requiring root cause identification, masking the underlying leak.
5. The notification service runs batch operations between 01:00–03:00 UTC (scheduled notifications), which accelerated the final memory accumulation phase.

---

## Resolution

1. Increased container memory limit from 512 MB to 1 GB as emergency mitigation (2:28 UTC) — extended service but did not fix the underlying leak.
2. Profiled memory usage with py-spy (`kubectl exec -it pod -- py-spy record`) to identify leak source.
3. Identified Jinja2 `_parse_cache` as the accumulation point.
4. Hotfix: replaced global `Environment` singleton with a per-render environment and explicit cache size limit.

```python
# notification-service — fixed
from jinja2 import Environment

def render_notification(template_str: str, context: dict) -> str:
    env = Environment(cache_size=0)  # No persistent cache for dynamic templates
    template = env.from_string(template_str)
    return template.render(**context)
```

5. Deployed hotfix as `notification-service v2.3.1`.
6. Verified memory stabilized at ~180 MB over 30 minutes of monitoring.
7. Reduced container memory limit back to 512 MB.
8. Processed notification backlog (1,240 queued notifications delivered within 15 minutes).

---

## Customer Impact

- **Notification delivery fully unavailable** for 4 hours 18 minutes (02:17–06:35 UTC).
- **Email notifications** (order confirmations, shipping updates) not delivered during window.
- **Push notifications** to mobile app not sent.
- **1,240 notification events** queued; delivered after resolution with up to 4+ hour delay.
- Direct customer impact minimal due to overnight window (low-traffic period).
- Internal SLA breach for two enterprise accounts that require sub-1-hour notification delivery.

---

## Preventive Actions

| Action | Owner | Due Date | Status |
|---|---|---|---|
| Fix: replace global Jinja2 Environment singleton with bounded cache | Notification Team | 2025-06-04 | Complete |
| Add memory growth rate alert: `memory increase > 50 MB/hour` over 30-min window | SRE Team | 2025-06-10 | Complete |
| Update CrashLoopBackOff runbook: require root cause identification before increasing memory limits | SRE Team | 2025-06-08 | Complete |
| Add memory profiling to the standard incident investigation toolkit | SRE Team | 2025-06-12 | In Progress |
| Run load tests for minimum 72 hours to detect memory leak patterns | QA Team | 2025-06-20 | Planned |
| Audit all services for unbounded global caches (template engines, regex, parsers) | Platform Team | 2025-06-25 | Planned |
| Implement graceful degradation: if notification-service is down, queue to SNS for retry | Notification Team | 2025-07-01 | Planned |

---

## Related Runbooks

- [RUN-K8S-001: CrashLoopBackOff Investigation and Recovery](../runbooks/RUN-K8S-001.md)
- [RUN-K8S-002: Kubernetes OOM Kill Response](../runbooks/RUN-K8S-002.md)
- [RUN-NOTIF-001: Notification Service Recovery](../runbooks/RUN-NOTIF-001.md)

---

## Lessons Learned

- Memory leaks in long-running services are time-bombs: they only manifest in production, and only after enough accumulated runtime to exhaust the container limit. Load tests must be long enough (72+ hours) to surface slow leaks.
- "Increase the memory limit" is a mitigation, not a fix. Runbooks that default to this action without requiring root cause identification mask underlying problems and delay resolution — in this case by 2+ hours.
- Global singleton caches (Jinja2 Environment, regex compilation caches, in-memory LRU caches without size limits) must be reviewed for bounded growth behavior before being used in production services. An unbounded cache is an OOM waiting to happen.
- Container memory limits set from load test observations must include a safety margin for leak-prone subsystems. A limit set at "peak observed" provides zero headroom for gradual accumulation.
- Batch jobs (scheduled notifications at 02:00 UTC) often run under different load profiles than continuous traffic. Memory leak rates during batch operations can be 3–5× higher than steady-state, compressing the time to OOM significantly.
