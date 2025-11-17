# Secrets Registry and Rotation Policy

## Secret store

- Use managed Secret Manager (AWS Secrets Manager or HashiCorp Vault) with replication in all regions.
- Access via short-lived IAM roles bound to Kubernetes ServiceAccounts using IRSA / Workload Identity.
- Applications fetch secrets at startup through sidecar (`vault-agent`) and refresh every 6 hours.

## Registry

| Key | Description | Consumers | Rotation cadence |
|-----|-------------|-----------|------------------|
| `db/app-primary` | PostgreSQL app user credentials | Backend, Celery | 30 days |
| `db/reporting-ro` | Read-only replica user | Backend read endpoints | 90 days |
| `redis/app` | Redis auth token | Backend, Celery | 60 days |
| `jwt/signing` | Asymmetric JWT signing keypair | Backend only | 90 days with dual-publish |
| `crypto/webhook` | HMAC secret for webhooks | Backend | 180 days |
| `payments/stripe` | Stripe API keys + webhook secret | Backend | 60 days |
| `payments/paypal` | PayPal credentials | Backend | 60 days |
| `smtp/sendgrid` | SendGrid API key | Backend, worker email tasks | 30 days |
| `storage/s3-app` | S3 access/secret keys + session policy | Backend, Celery | 90 days |
| `observability/datadog` | API + app keys | Agents | 120 days |

### Environment matrix

| Secret key | Dev | Stage | Prod |
|------------|-----|-------|------|
| `db/app-primary` | `dev/db/app-primary` (lower privileges, sample data) | `stage/db/app-primary` | `prod/db/app-primary` |
| `db/reporting-ro` | optional | stage copy | prod copy |
| `redis/app` | yes | yes | yes |
| `jwt/signing` | dev-only key, rotated automatically | manual dual-publish | manual dual-publish |
| `crypto/webhook` | optional | yes | yes |
| `payments/*` | sandbox tokens | stage tokens | live tokens |
| `smtp/sendgrid` | sandbox | staging | production |
| `storage/s3-app` | dev bucket credentials | stage bucket | prod bucket |
| `observability/datadog` | dev org | stage org | prod org |

## Rotation procedure

1. Owner files change request with rotation schedule and blast radius analysis.
2. Secret regenerated via automation (Terraform + Vault module) with dual-write capability.
3. Applications reload secret through sidecar template without redeploy when possible; otherwise redeploy sequentially (Dev → Stage → Prod).
4. Verify health endpoints and synthetic checks before decommissioning old secret.
5. Archive rotation log in `security/secret-rotations/<date>.md` with sign-off.

## Guardrails

- Secrets never stored in git, Dockerfiles, CI logs, or baked into images. Use build-time args referencing secret IDs only.
- IAM policies follow least privilege; e.g., backend role can read `db/*`, `jwt/*`, but not `payments/*`.
- Access reviews occur quarterly; break-glass credentials kept offline and rotated after every use.
- All secret changes emit audit events to SIEM with user, secret path, and hash fingerprint.

