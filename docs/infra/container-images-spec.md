# Container Images Specification

## Image catalog

| Image | Purpose | Base | Entrypoint | Healthcheck |
|-------|---------|------|------------|-------------|
| `registry.example.com/app/backend` | Django ASGI app server (uvicorn workers) | `python:3.12-slim` | `uvicorn config.asgi:application --host 0.0.0.0 --port 8000` | `/bin/grpc_health_probe` or HTTP `/healthz?deep=false` |
| `registry.example.com/app/worker` | Celery worker handling async jobs + beat | `python:3.12-slim` | `celery -A config worker --loglevel=info` | Celery ping script via `/bin/health-celery` |
| `registry.example.com/app/frontend` | Static assets produced by Vite/Next build | `node:20-alpine` (builder) + `caddy:2-alpine` (runtime) | `caddy run --config /etc/caddy/Caddyfile` | HTTP GET `/healthz` served by Caddy |
| `registry.example.com/app/nginx` | Edge reverse proxy / Ingress controller image | `nginx:1.25-alpine` | `nginx -g 'daemon off;'` | `CMD-SHELL curl -f http://localhost:8080/healthz || exit 1` |

## Naming convention

```
<registry>/<org>/<service>[:<tag>]
```

- `registry` — default `registry.example.com` (backed by ECR/GCR).
- `org` — `app` for first-party services, `ops` for infra images.
- `service` — `backend`, `worker`, `frontend`, `nginx`.
- Optional suffixes like `-debug` must never be pushed to production registries.

## Tagging policy

| Tag type | When used | Example |
|----------|-----------|---------|
| `latest` | Only in Dev for convenience; never promoted | `registry.example.com/app/backend:latest` |
| Git SHA | Every build, immutable | `registry.example.com/app/backend:sha-9f2c1ab` |
| SemVer | Stage/Prod releases, matches git tag `vX.Y.Z` | `registry.example.com/app/backend:v1.3.0` |
| Date tag | Nightly security rebuilds | `registry.example.com/app/backend:2024-05-30` |

Promotion rules:

1. Builds run once per merge via CI, producing SBOM + vulnerability report.
2. Artifacts promoted between environments without rebuild by retagging the same digest.
3. If Trivy reports High/Critical vulnerabilities, the pipeline fails and images are not pushed.

## SBOM and scanning

- Use `syft` to generate SPDX JSON SBOM stored as build artifact (`sbom/<image>-<sha>.spdx.json`).
- Scan images with `trivy image --severity HIGH,CRITICAL --exit-code 1` before push.
- Store reports in `artifacts/scans/` for 30 days.

## Hardening requirements

- Multi-stage builds remove build tooling before release stage.
- Non-root user `app` (UID 10001) runs the process; fs permissions tightened.
- Only required ports are exposed (8000 backend, 8001 worker metrics, 4173 dev server optional, 8080 nginx).
- Read-only root FS enabled at runtime except writable `/tmp`.

