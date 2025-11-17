# Load Test Report & Optimization Plan

## Scenario Summary
- **Profile**: +30% concurrent users (baseline 5k → test 6.5k).
- **Mix**: 60% browsing, 20% chat, 15% escrow ops, 5% payouts.
- **Tools**: k6 + WebSocket plugin, Locust for Celery API, S3 presigned upload simulation.
- **Duration**: 2h ramp + 1h steady + 30m soak.

## Results vs SLO
| Metric | SLO | Observed | Status |
| --- | --- | --- | --- |
| API availability | 99.9% | 99.93% | ✅ |
| API p95 latency | <300 ms | 320 ms | ⚠️ (needs tuning) |
| WS p95 latency | <1 s | 0.8 s | ✅ |
| Queue depth fast | <500 | 420 | ✅ |
| Queue depth heavy | <100 | 160 | ❌ |
| Replica lag | <10 s | 6 s | ✅ |
| Redis memory | <70% | 72% | ⚠️ |

## Bottlenecks
1. `search.listings` endpoint spends 180 ms in DB due to missing composite index.
2. Heavy payouts queue blocked by PSP sandbox 429 errors, causing retries and backlog.
3. Redis eviction warnings when media workers spike memory due to large payload caching.

## Optimization Plan
- Add partial index `CREATE INDEX CONCURRENTLY listings_locale_category_idx ON listings(locale, category) WHERE status='published';`.
- Split `heavy_payouts` queue into `payouts_high` (instant) and `payouts_bulk` (batch) with dedicated workers.
- Enable Redis `maxmemory-policy=allkeys-lru` with key TTL enforcement; move large media presign caches to DynamoDB.
- Implement adaptive rate-limiting when PSP returns 429 (pause 60s) to prevent cascading retries.
- Increase Celery worker autoscaling thresholds (HPA) to add pods when queue >80 for 3 minutes.
- Profile API CPU usage; plan for NodeGroup scale-out (add 2 nodes) before next peak.

## Follow-Up Actions
- Re-run load test after index + queue split; target completion in 2 weeks.
- Document PSP sandbox limits and align with finance team.
- Update Grafana dashboard with new Redis memory panels.
