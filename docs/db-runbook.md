# Database Runbook

## Topology and Objectives
- **Primary**: PostgreSQL 15 on managed service with PITR enabled (7-day WAL retention) and daily full backups at 02:00 UTC.
- **Standby**: Hot replica in another AZ with streaming replication; synchronous mode in prod, async elsewhere.
- **Backups**: `pg_basebackup` full snapshot + continuous WAL archiving to S3-compatible storage; verify checksums daily.
- **RTO/RPO targets**: RTO 15 minutes, RPO 5 minutes using WAL shipping.

## PITR and Backup Operations
1. Full backup pipeline (`pg_basebackup`) runs daily, uploads tarball to `s3://obsidian-db-backups/YYYY/MM/DD/` and registers in backup catalog.
2. WAL archiver streams to the same bucket in `wal/` prefix with object lock of 7 days.
3. PITR restore drill:
   ```bash
   # fetch base backup
   aws s3 sync s3://obsidian-db-backups/2025/02/10/base /var/lib/postgresql/restore
   # fetch WALs for target timestamp
   aws s3 sync s3://obsidian-db-backups/wal /var/lib/postgresql/restore_wal
   # recovery.conf
   restore_command = 'aws s3 cp s3://obsidian-db-backups/wal/%f %p'
   recovery_target_time = '2025-02-10 11:52:00+00'
   ```
4. Document restore result in incident log and rotate credentials after drill.

## Replica Lag Monitoring
- Query replica: `SELECT now() - pg_last_xact_replay_timestamp() AS replay_lag;`
- Alert at >5s warning, >30s critical (Surfaced in Grafana “DB & Redis”).
- Run `SELECT * FROM pg_stat_replication;` on primary to ensure `state='streaming'` and `sync_state='sync'`.

## Hot Standby Promotion
1. Confirm replica caught up (`replay_lag < 5s`).
2. `touch /var/lib/postgresql/15/main/trigger.promote` or `SELECT pg_promote(true, 300);`.
3. Update HAProxy/PG Bouncer targets + rotate connection strings in Vault.
4. Run smoke tests (`python manage.py check`, read/write sample) before declaring primary.

## Autovacuum, Indexing, and Connection Policy
- Autovacuum tuned per table: default scale factor 0.1, freeze age alerts at 150M. Add table overrides in `ALTER TABLE ... SET (autovacuum_vacuum_scale_factor=0.02)` for chat messages.
- Index review quarterly; enforce migration template requiring `CONCURRENTLY` on prod indexes.
- Connection limits: Postgres `max_connections=300`; prod uses PgBouncer in transaction pooling mode with 50 app connections; Celery workers use separate pool of 20 connections; analytics jobs use readonly replica DSN.

## Zero-Downtime Migration Flow
1. **Prepare**: Align product requirements with schema contract and feature flags.
2. **Expand**:
   - Create backward-compatible columns/tables (nullable, default values) via migration labelled `expand`.
   - Add indexes with `CONCURRENTLY` and gated DB constraints (NOT VALID) to avoid locking.
   - Deploy backend that can read/write both old and new schema pieces using feature flags.
3. **Backfill**:
   - Run managed `Celery` batch or SQL script under `feature_flag=backfill_enabled` to migrate historical rows in small batches (`LIMIT 10k`, `sleep 500ms`).
   - Track progress in `schema_migrations_audit` table.
4. **Verify**: Compare row counts, run read-only checks in replica, ensure dashboards show no error-rate spikes.
5. **Contract**:
   - Flip read path to new column via feature flag; monitor for 24h.
   - Drop unused columns/constraints/indexes in maintenance window with lock-time budget.
6. **Automation**: `ci/scripts/run_migrations.sh` enforces `expand/backfill/contract` directory naming; prod deploy runs `python manage.py migrate --plan` and requires operator approval for `contract` steps.

## Application-Aware Feature Flags
- Every migration feature toggled through LaunchDarkly keys (`db.expand.<ticket>`, `db.contract.<ticket>`).
- API code must be backward compatible for at least one full release cycle (2 weeks).

## Running Migrations
1. Check replica lag (<5s) and ensure PgBouncer pools drained (`SHOW POOLS;`).
2. Run `python manage.py migrate --plan` → share output in #release channel.
3. Execute migrations during CI deploy stage (before canary) using `./ci/run_safe_migrations.sh`.
4. For long-running migrations use `django-migration-linter` to enforce safe patterns and `pg_online_schema_change` when necessary.

## Restore Drill Playbook
1. Trigger drill quarterly from Infra calendar.
2. Provision temporary VPC + PostgreSQL instance.
3. Perform PITR using latest base backup + WAL to target time from incident simulation.
4. Run acceptance tests: checksum critical tables, `SELECT count(*)` comparisons vs production snapshot.
5. Document findings in `docs/db-restore-guide.md` and update runbook if gaps discovered.

## Troubleshooting Checklist
- Spikes in `pg_stat_activity`: enable query sampling, kill idle-in-transaction sessions >5m.
- Bloat >20%: run `pg_repack` on replica then switchover.
- Autovacuum not keeping up: temporarily increase `autovacuum_max_workers` to 8 and `maintenance_work_mem`.
