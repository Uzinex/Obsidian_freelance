# Data Retention and Privacy Policy

This policy covers production systems that store personal or financial data. Every product squad must map new datasets to a classification tier before shipping to production.

## 1. Data classification

| Class | Examples | Storage systems | Retention target |
| --- | --- | --- | --- |
| **PII** | Account profile (`accounts_user`, `profiles_profile`), contact info, device identifiers. | PostgreSQL, Redis session cache. | Active lifecycle + 24 months after last activity. |
| **KYC** | Secure documents (`uploads_securedocument`), AML notes, verification metadata. | PostgreSQL, S3 `kyc-docs` bucket (private). | 5 years (regulatory) + 90-day purge buffer. |
| **Financial** | Contracts (`marketplace_contract`), wallet transactions (`accounts_wallettransaction`), payouts. | PostgreSQL, data warehouse. | 10 years (audit). |
| **Logs & telemetry** | `accounts_auditevent`, API request logs, Prometheus, Sentry breadcrumbs. | PostgreSQL, Loki, ClickHouse. | 30 days raw, 180 days aggregated. |

## 2. Retention schedule and automated purges

| Dataset | Job/Mechanism | Frequency |
| --- | --- | --- |
| Dormant accounts | `manage.py purge_inactive_accounts --older-than=24m` deletes unverified profiles, anonymizes usernames/emails, and preserves audit trail IDs. | Weekly |
| KYC documents | `SecureDocument.purge_expired()` invoked by the `kyc-retention` Celery beat task removes file blobs from S3 and wipes metadata except document ID. | Daily |
| Logs | Loki retention policy enforces 30 days for labels containing `pii=false`. Aggregated metrics roll up via ClickHouse TTL tables. | Continuous |
| Media uploads | Versioned objects (`media/`) older than 18 months are removed by the `media-snapshot` job after a final S3 snapshot. | Daily |

Purges must **also** remove corresponding backups (see Section 4). When a record is deleted, a tombstone entry with hash-only identifiers is stored in `compliance_deletedrecord` to prove action.

## 3. Access controls

- KYC and financial datasets require the `moderator`, `staff`, or `finance` roles enforced via `accounts.rbac`. API endpoints must include `RoleBasedAccessPermission` checks with `rbac_action_map` mapping to `kyc:*` or `finance:*` actions.
- Access events are logged in `accounts_auditevent` with metadata identifying the actor, device, path, and reason code.
- Production support requires break-glass approval; elevated access expires automatically after 8 hours via IAM permission sets.

## 4. Backups and replicas

| Dataset | Backup mechanism | Retention |
| --- | --- | --- |
| PostgreSQL | PITR via `wal-g backup-push` (see `infra/k8s/cronjobs-backups.yaml`). Base backup daily + WAL archiving every 5 minutes. | 30 days. |
| Object storage | Daily S3 snapshot of `media/` and `kyc-docs/` buckets into encrypted vault with 35-day retention and bucket-level object lock. | 35 days. |
| Terraform/IaC | Nightly export of Terraform state + Kubernetes manifests stored in `s3://obsidian-iac-archive`. | 90 days. |

Backups containing deleted PII must be purged within 30 days of the deletion request.

## 5. Privacy requests

### 5.1 Right to be forgotten

1. Support creates a ticket with the user’s UUID and verifies identity using existing KYC.
2. Run `manage.py anonymize_user --user-id <uuid>` which:
   - Soft deletes the Django user and profile.
   - Redacts chat messages, contracts, and notifications by replacing message bodies with "[deleted]" while keeping numeric IDs.
   - Enqueues deletion of uploads + S3 objects.
3. Confirm audit logs contain only hashed identifiers (see Section 6) and close the ticket once the background jobs finish (< 24h SLA).

### 5.2 Data export (ZIP)

1. Call `GET /api/accounts/export` (staff-only) or trigger the self-service portal. The exporter serializes profile, contracts, payouts, and chat history into JSON files.
2. Files are zipped, encrypted with a one-time key, and uploaded to the `user-exports` bucket. The user receives an expiring download link (48h).

## 6. Logging and PII masking

- Application audit logs go through the sanitizer implemented in `backend/accounts/audit.py` and enforce `pii=false` labels before shipping to Loki.
- Structured logging forbids storing raw email, phone, document numbers, or card PANs. Use hashed IDs or last4 tokens only.
- Sentry is configured with `send_default_pii=False` for non-staff environments.

## 7. Monitoring & review

- Weekly compliance report verifies purge metrics, pending privacy requests, and any open access review items.
- Quarterly tabletop exercises validate the deletion/export process end-to-end.

