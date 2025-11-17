# Ops Handbook

## Run-Books

### Deploy / Rollback
1. Confirm `main` is green in CI and the release checklist is signed off.
2. Tag the release, push tags, and trigger the `deploy-prod` pipeline.
3. Monitor deployment dashboard (ArgoCD & GitHub Actions) for drift.
4. If a rollback is needed, redeploy previous stable tag via the same pipeline and re-run smoke tests.
5. Announce status in #ops-alerts, including ticket links.

### Database Migrations
1. Review migration plan in `docs/db-migrations.md` and ensure backward-compatible code is in prod.
2. Enable `safe-migrations` flag in pipeline; run migrations via `make migrate-prod`.
3. Monitor replication lag (<100 ms) and slow queries (<200 ms) in Grafana dashboard `DB/Prod`.
4. If anomalies occur, pause rollout, revert schema via `rollback_plan.md`, and notify BE lead.

### DB / Redis / CDN Outages
1. Check uptime monitor to confirm scope. Use `kubectl get pods -n data-plane` for DB/Redis health.
2. Fallback to read replicas / secondary Redis cluster by flipping `DB_READONLY_ENDPOINT` or `REDIS_SECONDARY`.
3. For CDN, invalidate problematic POP, switch traffic to backup provider using Terraform variable `cdn_active_provider`.
4. Update status page within 15 minutes and open incident channel.

### PSP Webhook Failures
1. Inspect webhook retries queue (`queues-and-retries-matrix.md`).
2. Re-send failed events using `scripts/replay_psp_webhooks.py --event-id <id>`.
3. Coordinate with Payments team to validate signatures and PSP status pages.
4. If PSP is degraded, throttle payout creation and communicate ETA to Support.

### Secret / Key Leak
1. Rotate affected key following `secrets_policy.md`.
2. Revoke compromised credentials (AWS/K8s/PSP) and deploy new sealed secrets.
3. Force logout tokens via `auth/InvalidateSessions` job.
4. File security incident, perform postmortem, and update secret-scanning rules.

## Where to Look
- **Logs:** Loki `prod/*`, application structured logs in Datadog (`service:core-*`).
- **Metrics:** Grafana dashboards (Service Overview, DB/Prod, Redis/Cache, CDN Health) and Datadog SLO widgets.
- **Traces:** OpenTelemetry via Tempo; filter by `env:prod` and `trace.flow_id` for disputes/payments.

## Ownership Matrix
| Domain | Primary | Backup |
| --- | --- | --- |
| DevOps/SRE | @sre-lead | @sre-oncall |
| Backend | @be-lead | @be-oncall |
| Frontend | @fe-lead | @fe-oncall |
| Payments | @payments-lead | @payments-oncall |
| Support | @support-manager | @support-lead |
