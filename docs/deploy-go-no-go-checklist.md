# Deploy Go/No-Go Checklist

## Pre-Deploy
- [ ] Release notes reviewed, Jira tickets closed, feature flags mapped.
- [ ] SBOM + vulnerability scan passed (no critical/high findings outstanding).
- [ ] DB migrations categorized (expand/backfill/contract) and dry-run executed on Stage.
- [ ] Replica lag < 5s, PgBouncer pools healthy, Redis memory < 70%.
- [ ] Backups verified within last 24h; WAL archiving enabled.
- [ ] On-call engineer paged-in and aware of rollout plan.
- [ ] Rollback artifact available (previous image tag + DB snapshot).

## Stage Validation
- [ ] Stage deploy succeeded, automated smoke tests green.
- [ ] Feature toggles configured for Stage.
- [ ] Synthetic monitoring scenario run via staging environment and meeting SLO.

## Manual Approval Gate
- [ ] Change request approved by product/QA.
- [ ] No open Sev1/Sev2 incidents.
- [ ] Security sign-off if new scopes/secrets introduced.

## Production Canary
- [ ] Canary receiving 10% traffic and API p95 < 300 ms for 15 minutes.
- [ ] Error rate < 1%, queue depth stable, DB replica lag < 10s.
- [ ] Automated migration verification script reports success.

## Full Rollout
- [ ] Blue/Green flip executed, old stack kept warm for 30 minutes.
- [ ] CDN invalidations triggered for static/media updates.
- [ ] Celery workers drained/restarted with new image.

## Post-Deploy
- [ ] RUM dashboards checked for regression within 1 hour.
- [ ] Go/No-Go status posted in #releases with key metrics screenshot.
- [ ] Incident template prepared if rollback triggered.
- [ ] Schedule post-release retro if anomalies observed.
