# INC-2025-003 — Redis Cache Failure and Cache Stampede

| Field | Value |
|---|---|
| **Incident ID** | INC-2025-003 |
| **Date** | 2025-04-19 |
| **Severity** | SEV2 |
| **Duration** | 2 hours 11 minutes |
| **Status** | Resolved |
| **Incident Commander** | Sunita Rao |
| **Affected Services** | product-catalog-service, recommendation-engine, search-service, redis-cache-cluster |
| **Document Type** | postmortem |

---

## Executive Summary

On April 19, 2025, a Redis primary node failure in the product catalog cache cluster triggered a cache stampede that overwhelmed the PostgreSQL product database, causing elevated latency and partial unavailability of product catalog, recommendations, and search features for 2 hours and 11 minutes. The Redis primary (redis-cache-01) failed due to an out-of-memory (OOM) kill at 11:04 UTC. Redis Sentinel promoted a replica within 45 seconds, but the brief loss of the primary flushed the in-memory cache state of downstream services. When all 12 product-catalog-service instances simultaneously attempted to repopulate the cache from the database, the resulting thundering herd of queries — approximately 14,000 queries/second — caused PostgreSQL query latency to spike from 8 ms to 4,200 ms, cascading into timeout errors across the catalog, recommendation, and search pipelines.

---

## Timeline

| Time (UTC) | Event |
|---|---|
| 11:04 | redis-cache-01 OOM-killed by Linux kernel (memory: 7.9 GB / 8 GB limit) |
| 11:04 | Redis Sentinel detects primary failure |
| 11:04:45 | redis-cache-02 promoted to primary by Sentinel |
| 11:05 | All 12 product-catalog-service instances detect cache miss (empty replica) |
| 11:05 | Cache stampede begins: 14,000 queries/second hit PostgreSQL |
| 11:07 | PagerDuty alert: `product_catalog_p99_latency > 2000ms` |
| 11:09 | PagerDuty alert: `recommendation_engine_error_rate > 10%` |
| 11:11 | Incident Commander engaged, SEV2 declared |
| 11:18 | Root cause identified: cache stampede post-Redis failover |
| 11:25 | Manual rate limiting applied: product-catalog queries throttled to 500 QPS per instance |
| 11:45 | Cache warming script executed: top 50,000 product records pre-loaded into Redis |
| 12:03 | PostgreSQL query latency returns to baseline |
| 13:15 | All services fully recovered, alerting normalized |

---

## Root Cause

**Primary:** Redis primary OOM kill caused by unbounded memory growth from uncontrolled key TTL distribution. A data migration job run at 10:30 UTC loaded 2.1 million new product variant keys into Redis with a fixed 24-hour TTL and no `maxmemory-policy` eviction configured. When the migration job completed, Redis memory crossed the 8 GB container limit, triggering an OOM kill.

**Secondary (Cache Stampede):** The product-catalog-service did not implement mutex locking or probabilistic early expiration for cache population. When all instances lost their local cache simultaneously, each independently queried the database for the same records, causing a thundering herd.

**Contributing Factors:**

1. Redis `maxmemory-policy` was set to `noeviction` (default), meaning Redis accepted all writes until OOM rather than evicting old keys.
2. The data migration job was run during business hours without coordination with the SRE team.
3. No Redis memory growth alert existed.
4. Cache stampede protection (mutex / probabilistic refresh / stale-while-revalidate) was never implemented.
5. PostgreSQL connection pool for catalog reads was sized for cached traffic (low QPS), not for full cold-start load.

---

## Resolution

1. Redis Sentinel promoted replica to primary automatically (within 45 seconds).
2. Applied manual query throttling to product-catalog-service to reduce thundering herd impact while cache was being repopulated.
3. Ran cache warming script to pre-populate the 50,000 most frequently accessed product records.
4. Monitored PostgreSQL latency and Redis memory over 30 minutes post-warming.
5. Issued all-clear once p99 latency returned to below 50 ms.

---

## Customer Impact

- Product catalog pages showed **partial data or failed to load** for 2 hours 11 minutes.
- Recommendation sections on product pages were **completely unavailable**.
- Search latency increased by **8×** for the duration.
- Approximately **41,000 user sessions** affected.
- Estimated revenue impact: $76,000 in lost browsing-to-purchase conversion.

---

## Preventive Actions

| Action | Owner | Due Date | Status |
|---|---|---|---|
| Set Redis `maxmemory-policy` to `allkeys-lru` on all cache clusters | SRE Team | 2025-04-25 | Complete |
| Add Redis memory utilization alert at 70% threshold | SRE Team | 2025-04-22 | Complete |
| Implement mutex locking (Redis SETNX) for cache population in product-catalog-service | Catalog Team | 2025-05-10 | In Progress |
| Implement stale-while-revalidate pattern for high-traffic catalog keys | Catalog Team | 2025-05-15 | Planned |
| Require SRE approval for data migration jobs touching shared caches > 100 MB | Platform Team | 2025-04-28 | Complete |
| Right-size PostgreSQL connection pool for cold-start scenarios | DBA Team | 2025-05-01 | In Progress |
| Create automated cache warming procedure for Redis failover events | SRE Team | 2025-05-20 | Planned |

---

## Related Runbooks

- [RUN-REDIS-001: Redis Cluster Failover Response](../runbooks/RUN-REDIS-001.md)
- [RUN-REDIS-002: Redis Connection Pool Exhaustion](../runbooks/RUN-REDIS-002.md)
- [RUN-CAT-001: Product Catalog Service Recovery](../runbooks/RUN-CAT-001.md)
- [RUN-DB-003: PostgreSQL Thundering Herd Mitigation](../runbooks/RUN-DB-003.md)

---

## Lessons Learned

- `noeviction` is the wrong `maxmemory-policy` for cache clusters — use `allkeys-lru` or `volatile-lru` so Redis degrades gracefully under memory pressure rather than being OOM-killed.
- Data migration jobs that write large volumes of keys to shared caches must be coordinated with SRE and executed during off-peak hours.
- Cache stampede protection is not a performance optimization — it is a reliability requirement. A service that reads from a cache without stampede protection will cause database overload on every cold start or failover.
- Redis and PostgreSQL connection pooling must both be sized for worst-case load (full cold start), not steady-state cached load. The difference between these two load profiles can be 100×.
