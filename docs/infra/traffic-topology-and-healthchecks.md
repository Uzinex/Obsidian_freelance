# Traffic Topology and Health Checks

## Request flow

1. Client connects over HTTPS to CDN/WAF that terminates TLS 1.3 and enforces rate limits + bot rules.
2. CDN forwards to regional load balancer (L7) living in public subnet.
3. Load balancer routes to Kubernetes Ingress / Nginx pods.
4. Nginx terminates TLS (optional mTLS from CDN) and forwards to ASGI backend via HTTP/2 (h2c) with `proxy_pass` and sticky hashing on session cookies.
5. Background jobs expose metrics through ServiceMonitor scraped by Prometheus over the cluster network.

### Nginx/Ingress settings

- `keepalive_timeout 65s` and upstream keepalive pools of 256 connections to reduce TLS churn.
- `client_max_body_size 16m` for API, `64m` for uploads endpoint (override via annotation).
- `gzip on` and `brotli on` for static assets + JSON responses >1kB; ensure `Vary: Accept-Encoding` is set.
- Connection limits: `limit_req zone=api burst=40 nodelay; limit_conn addr 100;`.

## Health checks

| Component | Probe | Path | Frequency | Success criteria |
|-----------|-------|------|-----------|------------------|
| Nginx ingress | HTTP GET | `/healthz` (served by lua block) | every 10s | 200 OK, body `ok` |
| Backend pods | Kubernetes `readinessProbe` | `GET /healthz?deep=false` | period 5s, timeout 1s | HTTP 200 | 
| Backend pods | Kubernetes `livenessProbe` | `GET /healthz?deep=true` | period 15s | 200 + DB/Redis connectivity |
| Celery worker | `exec` probe | `/bin/health-celery` | 15s | exit 0 after `celery inspect ping` |
| Redis/Postgres | Managed service monitors | N/A | builtin | provider SLA |

### `/healthz` endpoint contract

- `GET /healthz?deep=false` (default) → returns JSON `{ "status": "ok", "ts": 123 }` once ASGI loop started.
- `GET /healthz?deep=true` → performs async checks:
  - Postgres `SELECT 1` using connection pool.
  - Redis `PING`.
  - Object storage signed `HEAD` request to `/healthcheck.txt`.
- Failures return `503` with reason codes for faster triage.

## Checklist

1. [ ] `/healthz` handler implemented in Django view + DRF router.
2. [ ] Nginx upstream config includes health endpoint exemptions from auth.
3. [ ] Prometheus scrape jobs created for ingress controller, backend, Celery metrics.
4. [ ] Synthetic tests hit Prod health endpoints from two regions every 1 minute.
5. [ ] Alerting policy: 3 consecutive readiness failures page SRE for Prod, Stage sends Slack warning.

