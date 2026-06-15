# INC-2025-004 — SQS Message Backlog and Order Processing Delay

| Field | Value |
|---|---|
| **Incident ID** | INC-2025-004 |
| **Date** | 2025-05-07 |
| **Severity** | SEV2 |
| **Duration** | 3 hours 42 minutes |
| **Status** | Resolved |
| **Incident Commander** | David Okonkwo |
| **Affected Services** | order-service, sqs-order-queue, lambda-order-processor, fulfillment-service, notification-service |
| **Document Type** | incident_report |

---

## Executive Summary

On May 7, 2025, an IAM permission misconfiguration introduced during a routine infrastructure rotation caused the Lambda-based SQS consumer (`lambda-order-processor`) to silently stop processing order messages. Messages accumulated in the SQS queue over 3 hours and 42 minutes before the backlog was detected and the issue resolved. During this window, no orders were processed or fulfilled. A backlog of 28,400 order messages accumulated. Customers received no order confirmations, shipment notifications, or fulfillment updates for the duration. The IAM role rotation process had removed the `sqs:ReceiveMessage` permission from the Lambda execution role without triggering any immediate error — Lambda simply stopped polling.

---

## Timeline

| Time (UTC) | Event |
|---|---|
| 06:15 | IAM role rotation job runs; `sqs:ReceiveMessage` permission inadvertently removed from `lambda-order-processor-role` |
| 06:15 | Lambda stops polling SQS queue; no error logged (Lambda is not triggered when it cannot read) |
| 06:15 | SQS message backlog begins growing silently |
| 06:45 | First orders from the morning peak begin failing to confirm |
| 07:30 | Customer support receives first complaints about missing order confirmations |
| 08:30 | Customer support volume reaches 10× normal; escalated to engineering |
| 09:10 | Engineering investigation begins; order-service shows healthy (orders successfully enqueued to SQS) |
| 09:22 | SQS queue depth metric examined: 18,700 messages queued, 0 messages processed since 06:15 |
| 09:31 | Lambda invocation count metric: 0 invocations since 06:15 |
| 09:40 | IAM policy diff reviewed; missing `sqs:ReceiveMessage` identified |
| 09:47 | IAM permission restored |
| 09:50 | Lambda begins processing backlog |
| 09:57 | Incident declared resolved; backlog processing estimated to complete in 4 hours |

---

## Root Cause

**Primary:** The IAM role rotation automation script that runs weekly to rotate Lambda execution roles contained a bug: when generating the new role policy from a JSON template, it omitted `sqs:ReceiveMessage` from the permissions list. This was introduced in an update to the automation script in PR #2241 three weeks prior.

The permissions template `lambda-order-processor-policy.json.j2` had:

```json
{
  "Action": [
    "sqs:SendMessage",
    "sqs:DeleteMessage",
    "sqs:GetQueueAttributes"
  ]
}
```

The `sqs:ReceiveMessage` action was present in the original manually-created policy but absent from the Jinja2 template that the rotation script used to regenerate the policy, meaning every rotation cycle overwrote the live policy with an incomplete one.

**Contributing Factors:**

1. Lambda's SQS trigger model is pull-based: if Lambda cannot receive messages, it simply stops polling with no error or alert.
2. No alarm existed on `SQS ApproximateNumberOfMessagesNotVisible` or `ApproximateAgeOfOldestMessage`.
3. IAM policy rotation was not followed by automated validation testing (e.g., a canary that verifies Lambda can successfully read from SQS).
4. The bug had been present for three rotation cycles but was never triggered because the `sqs:ReceiveMessage` permission was correctly present in a separate inline policy (which is now gone, merged into the managed policy).

---

## Resolution

1. Confirmed Lambda invocation count was zero since 06:15 via CloudWatch.
2. Correlated zero invocations with IAM role rotation job at 06:15 via audit logs.
3. Compared live IAM policy with expected policy — identified missing `sqs:ReceiveMessage`.
4. Added `sqs:ReceiveMessage` back to the Lambda execution role's SQS policy.
5. Lambda immediately resumed polling; backlog processing began.
6. Monitored backlog drain rate and customer notification delivery.
7. Backlog fully processed by 14:30 UTC; all order confirmations delivered with explanation email to affected customers.

---

## Customer Impact

- **28,400 order messages** unprocessed for up to 3 hours 42 minutes.
- **0 order confirmations** sent during the outage window.
- **0 shipment notifications** triggered.
- Fulfillment delays for all orders placed between 06:15–09:57 UTC.
- Customer support received **1,840 tickets** during the incident.
- Escalations from **14 enterprise accounts** with SLA guarantees.
- Estimated SLA credit exposure: $22,000.

---

## Preventive Actions

| Action | Owner | Due Date | Status |
|---|---|---|---|
| Fix IAM policy template: add `sqs:ReceiveMessage` to `lambda-order-processor-policy.json.j2` | Platform Team | 2025-05-08 | Complete |
| Add post-rotation validation: synthetic test that verifies Lambda can read from SQS | Platform Team | 2025-05-14 | Complete |
| Add CloudWatch alarm on `ApproximateAgeOfOldestMessage > 5 minutes` for order queue | SRE Team | 2025-05-09 | Complete |
| Add CloudWatch alarm on Lambda invocation count dropping to 0 during business hours | SRE Team | 2025-05-09 | Complete |
| Implement dead-letter queue with alerting for messages that fail processing | Order Team | 2025-05-20 | In Progress |
| Audit all IAM policy templates for missing permissions compared to live policies | Security Team | 2025-05-21 | In Progress |
| Add integration test for order processing pipeline end-to-end in staging | Order Team | 2025-06-01 | Planned |

---

## Related Runbooks

- [RUN-ORDER-001: Order Processing Pipeline Recovery](../runbooks/RUN-ORDER-001.md)
- [RUN-SQS-001: SQS Queue Backlog Drain Procedure](../runbooks/RUN-SQS-001.md)
- [RUN-IAM-001: IAM Permission Audit and Restoration](../runbooks/RUN-IAM-001.md)

---

## Lessons Learned

- Pull-based consumers (Lambda/SQS, Kafka consumers) fail silently when deprived of read permissions — they simply stop consuming without logging errors. Backlog accumulation alarms are the only reliable early detection mechanism.
- IAM policy automation scripts require the same review and test rigor as application code. A missing permission in a template is a latent production bug that only surfaces on the next rotation cycle.
- End-to-end pipeline health must be monitored, not just individual components. Order-service was healthy, Lambda was healthy, SQS was healthy — yet no orders were processed. Component-level health checks missed a broken integration.
- Proactive SQS queue depth alerting with a low threshold (5 minutes age for highest-priority queues) would have reduced MTTR from 3+ hours to under 20 minutes.
