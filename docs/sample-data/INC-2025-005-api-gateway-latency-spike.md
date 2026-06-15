# INC-2025-005 — API Gateway Latency Spike

| Field | Value |
|---|---|
| **Incident ID** | INC-2025-005 |
| **Date** | 2025-05-22 |
| **Severity** | SEV2 |
| **Duration** | 58 minutes |
| **Status** | Resolved |
| **Incident Commander** | Elena Vasquez |
| **Affected Services** | api-gateway, product-service, inventory-service, pricing-service |
| **Document Type** | rca |

---

## Executive Summary

On May 22, 2025, a latency spike on the API Gateway caused p99 response times to increase from 120 ms to over 9,000 ms for all product-detail API endpoints. The incident lasted 58 minutes and affected all clients consuming the product detail API — mobile apps, web frontend, and third-party partner integrations. Root cause was an N+1 query pattern introduced in `product-service v4.1.0`, deployed at 10:05 UTC. The new "enriched product detail" endpoint resolved inventory availability and pricing for each product variant individually rather than batching the lookups, generating up to 47 downstream service calls per request under realistic catalog conditions. Under production load, this caused the inventory-service and pricing-service to become the latency bottleneck, with upstream API Gateway requests timing out.

---

## Timeline

| Time (UTC) | Event |
|---|---|
| 10:05 | Deployment of `product-service v4.1.0` (new enriched product detail endpoint) |
| 10:12 | p99 API Gateway latency begins climbing: 120 ms → 800 ms |
| 10:15 | PagerDuty alert: `api_gateway_p99_latency > 2000ms` |
| 10:17 | Incident Commander engaged |
| 10:21 | Inventory-service CPU: 94% (normal: 25%) |
| 10:23 | Pricing-service request queue depth: 12,000 pending requests |
| 10:28 | Trace analysis in Jaeger identifies N+1 call pattern in product-service |
| 10:35 | Decision: roll back product-service to v4.0.9 |
| 10:41 | Rollback deployed |
| 10:50 | Inventory-service and pricing-service load normalizing |
| 11:03 | p99 latency returns to 130 ms baseline |
| 11:05 | Incident resolved |
| 11:30 | Detailed performance analysis shared with product-service team |

---

## Root Cause

**Primary:** The new `GET /api/v1/products/{id}/enriched` endpoint in `product-service v4.1.0` implemented an N+1 query pattern across downstream services. For a product with N variants, the code made:

- N calls to `inventory-service` (one per variant)
- N calls to `pricing-service` (one per variant)

For a product page displaying 47 variants (the average for clothing items), this generated 94 downstream service calls per inbound request.

```python
# product-service v4.1.0 — the N+1 implementation
async def get_enriched_product(product_id: str) -> EnrichedProduct:
    product = await product_repo.get(product_id)
    for variant in product.variants:
        variant.inventory = await inventory_client.get(variant.sku)  # N calls
        variant.price = await pricing_client.get(variant.sku)        # N calls
    return product
```

Under 500 concurrent product-detail requests (normal production load), this generated 47,000 downstream calls/second to inventory-service and pricing-service — 18× their normal load.

**Contributing Factors:**

1. Performance testing in staging was conducted with a single-variant product fixture. The N+1 pattern only manifests under multi-variant product load.
2. No distributed tracing (Jaeger) sampling was enabled in staging, so the call pattern was not visible pre-deployment.
3. The enriched endpoint was added to handle a new mobile app feature but was also inadvertently wired as the default response for all product-detail requests (not behind a feature flag).
4. No rate limits existed on inter-service HTTP calls within the product service mesh.

---

## Resolution

1. Distributed trace analysis in Jaeger identified the N+1 call pattern within 6 minutes of investigation start.
2. Rolled back product-service to v4.0.9 to restore baseline behavior.
3. Monitored inventory-service and pricing-service request queue drain post-rollback.
4. Created fix branch: batched inventory and pricing lookups using bulk endpoints (`/inventory/batch`, `/pricing/batch`).
5. Fixed version deployed as v4.1.1 after performance validation at staging with a 47-variant product fixture.

---

## Customer Impact

- All product-detail API consumers experienced **p99 latency > 9 seconds** for 58 minutes.
- Mobile app: product pages effectively **unresponsive** (10-second hard timeout).
- Web frontend: product detail pages loading slowly or failing.
- **3 partner integrations** triggered circuit breakers and showed fallback content.
- Cart abandonment rate increased by **34%** during the incident window.
- Estimated revenue impact: $52,000 in abandoned carts.

---

## Preventive Actions

| Action | Owner | Due Date | Status |
|---|---|---|---|
| Fix N+1 pattern: use batch endpoints for inventory and pricing lookups | Product Team | 2025-05-29 | Complete |
| Create multi-variant product fixtures (20, 47, 100 variants) for staging load tests | QA Team | 2025-05-27 | Complete |
| Enable distributed tracing in staging with 100% sampling for new endpoints | Platform Team | 2025-05-28 | Complete |
| New endpoints must be behind feature flags until performance-validated | Product Team | 2025-05-26 | Complete |
| Add downstream call count per request as a custom metric with alert at 10 calls | SRE Team | 2025-06-05 | In Progress |
| Implement API rate limiting on internal service mesh for product-service | Platform Team | 2025-06-10 | Planned |
| Add code review checklist item: check for N+1 query/call patterns | Engineering Lead | 2025-05-27 | Complete |

---

## Related Runbooks

- [RUN-API-001: API Gateway Latency Spike Investigation](../runbooks/RUN-API-001.md)
- [RUN-PRODUCT-001: Product Service Rollback Procedure](../runbooks/RUN-PRODUCT-001.md)
- [RUN-TRACE-001: Distributed Tracing with Jaeger](../runbooks/RUN-TRACE-001.md)

---

## Lessons Learned

- N+1 query patterns in service-oriented architectures are a latency amplifier: one user-facing request becomes N×2 downstream calls. Load testing must use realistic data fixtures, not minimal test cases that mask the amplification factor.
- Feature endpoints that introduce new downstream call patterns should always be deployed behind feature flags and performance-tested under realistic multi-variant conditions before general availability.
- Distributed tracing with meaningful sampling rates in staging is the single most effective tool for catching N+1 patterns before they reach production. A trace that shows 94 spans for one request is an obvious red flag; a benchmark that shows "p50: 45 ms" on a one-variant fixture is not.
- Timeout cascades between services (API Gateway → product-service → inventory/pricing) are amplified by synchronous N+1 call chains. Bulkhead patterns and circuit breakers must be present at each hop to prevent cascading degradation.
