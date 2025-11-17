# Disaster Recovery Runbook & Drill Report

## 1. Objectives

- **RPO:** 15 minutes (WAL shipping cadence every 5 minutes with 3x redundancy).
- **RTO:** 2 hours (includes database restore + app redeploy + smoke tests).

## 2. Recovery checklist

1. Page the incident commander (IC) and declare DR event in PagerDuty.
2. Freeze deploys and capture current incident timeline in Statuspage.
3. Confirm scope: region-wide outage vs. application fault.
4. Pull the latest DR kit: Terraform variables, secrets bundle, and runbook copy.
5. Validate most recent WAL-G backup exists in `s3://obsidian-db-backups/latest/`.
6. Restore database (Section 3) and application stack (Section 4).
7. Run verification tests (Section 5).
8. Update stakeholders, lift deploy freeze, and schedule postmortem.

## 3. Database restore (PITR)

1. Provision a fresh PostgreSQL 15 instance with the same major version and storage profile.
2. Download the base backup from the DR bucket:
   ```bash
   aws s3 sync s3://obsidian-db-backups/base/2025-02-10 /restore/base
   aws s3 sync s3://obsidian-db-backups/wal/ /restore/wal --exclude "*" --include "2025-02-10*"
   ```
3. Configure `postgresql.conf`:
   ```ini
   restore_command = 'aws s3 cp s3://obsidian-db-backups/wal/%f %p'
   recovery_target_time = '<ISO8601 timestamp from incident - 15m>'
   ```
4. Start PostgreSQL in recovery mode and monitor `pg_wal` replay.
5. When recovery reaches target time, promote the instance (`pg_ctl promote`).

## 4. Application + media restore

1. Apply Terraform stack pointing to the DR region (variables: `region=eu-central-1-dr`).
2. Deploy Kubernetes manifests:
   ```bash
   kubectl apply -f infra/k8s/ingress-example.yaml
   kubectl apply -f infra/k8s/networkpolicy-egress.yaml
   kubectl apply -f infra/k8s/cronjobs-backups.yaml
   ```
3. Restore media:
   ```bash
   aws s3 sync s3://obsidian-media-snapshots/latest/ s3://obsidian-media-dr/ --delete
   ```
4. Run database migrations and warm up caches.

## 5. Verification tests

- `pytest backend --maxfail=1 --disable-warnings -k smoke`
- API health probes: `/healthz?deep=true`, `/api/accounts/login` (mock credentials), `/api/payments/ping`.
- Synthetic payments + webhook simulation to ensure egress and queue delivery.

## 6. Drill scenario (2025-02-10)

| Phase | Timestamp (UTC) | Notes |
| --- | --- | --- |
| Detection | 10:05 | AWS us-east-1 networking failure detected by synthetics. |
| Declared | 10:10 | IC paged, status page updated (API/Web degraded). |
| DB restore start | 10:15 | PITR initiated using base backup from 09:30 + WAL to 09:58. |
| App deploy | 10:40 | Terraform + ArgoCD deploy to eu-central-1 DR cluster. |
| Verification | 11:30 | Smoke tests passed; payments succeeded in sandbox. |
| Traffic switch | 11:40 | Cloudflare load balancer flipped to DR origin. |
| Close | 12:00 | RTO achieved (1h50m). Postmortem scheduled. |

## 7. Lessons learned (drill)

- Need faster S3 snapshot replication (optimize `aws s3 sync` concurrency).
- Automate cache warm-up via Job to reduce login latency during failover.
- Documented status page workflow in `docs/postmortem-template.md` and trained comms liaison.

