# Production Security Baseline

This baseline enumerates minimum controls that must exist in every production environment. Owners must document exceptions in the security risk register and obtain approval before deploying changes.

## 1. Perimeter controls

| Control | Implementation | Owner |
| --- | --- | --- |
| **WAF** | All public domains terminate at Cloudflare Enterprise with the OWASP Core Rule Set v4.5, managed rulesets for Log4Shell/Shellshock, and custom rules blocking high-risk countries. High-sensitivity paths (`/api/accounts/login`, `/api/accounts/reset`, `/api/payments/*`, `/api/webhooks/*`) run through a separate ruleset that enforces JS challenges for unauthenticated clients. For clusters without Cloudflare, the `infra/k8s/ingress-example.yaml` manifest enables the NGINX Ingress ModSecurity module with the same ruleset and per-path rate limits. | SRE |
| **Bot management** | Cloudflare Bot Management enforces behavior scoring and challenges clients with score < 30. Additionally, the ingress configuration checks `cf-threat-score`/`cf-bot-score` headers and drops requests that fail the allowlist. Static assets are served behind CDN Shield to avoid origin enumeration. | SRE |
| **Rate limiting** | Application-layer throttling lives in `backend/obsidian_backend/settings.py` (`DEFAULT_THROTTLE_CLASSES` covering login, reset, payments, uploads, chat). Perimeter throttling is configured via the ingress annotations (`limit-req` zones for login/payment/webhook paths) so credential-stuffing never reaches the app. | Backend + SRE |
| **Egress control** | Namespaces apply the `backend-egress-policy` NetworkPolicy (see `infra/k8s/networkpolicy-egress.yaml`) that only allows traffic to PostgreSQL, Redis, observability endpoints, and S3-compatible object storage CIDRs. Outbound internet is disabled unless the pod carries the `egress.obsidian.dev/allow-external: "true"` label reviewed by SRE. | Platform |

## 2. TLS and certificates

1. `cert-manager` provisions certificates via the `letsencrypt-prod` cluster issuer. The ingress manifest sets `cert-manager.io/cluster-issuer: letsencrypt-prod` so every certificate auto-renews 20 days before expiry.
2. TLS 1.2+ only. The ingress forces `TLSv1.2 TLSv1.3` and Mozilla "modern" cipher suites.
3. HTTP Strict Transport Security is set to one year with preload through `SecurityHeadersMiddleware` in the Django stack.
4. Automated certificate expiry alerts fire from Prometheus (`ssl_cert_not_after` < 30 days) and Cloudflare.

## 3. Dependency and container scanning

| Control | Tooling |
| --- | --- |
| SCA + IaC scanning | GitHub Advanced Security + `pip-audit` job on every PR. Fails CI if severity >= High remains unresolved. |
| Container scanning | `Trivy` runs in the `scan-container` job in CI for backend and worker images. Uploads SBOM + vulnerability report to Security Hub. |
| Merge gating | The `security-gate` workflow blocks merge/deploy when Trivy or Snyk report High/Critical findings without waivers stored in `security-waivers.yml`. |

## 4. Image policy

1. Build pipeline signs OCI images with `cosign` and stores attestations in the registry.
2. Admission Controller (Kyverno) validates signatures and rejects unsigned images.
3. `infra/k8s/networkpolicy-egress.yaml` prevents pods from exfiltrating data. To open an exception, teams must add explicit `to:` blocks referencing DNS/IPv4 targets and document the change in the security channel.

## 5. Secrets and supply chain

- Secrets live in AWS Secrets Manager and sync into clusters through External Secrets; service accounts receive least-privilege IAM roles.
- Dockerfiles pin digest versions and run `apt-get` with `--no-install-recommends` to shrink the attack surface.
- Base images come from the golden repository and are refreshed monthly.

## 6. Status page and comms alignment

- Uptime is published on https://status.obsidian.io. Components: API, Web, Payments, Webhooks, DB, CDN. Each component maps to Prometheus/SLO alerts.
- PagerDuty incidents automatically update the status page via the Statuspage.io integration; the fallback is a 15-minute manual update cadence by the incident commander.
- Communication templates (initial/update/resolved) are stored in `docs/postmortem-template.md` and must be copied into Statuspage + customer emails.

## 7. Audits and evidence

- Quarterly SRE review attaches screenshots/logs proving WAF, TLS, scan jobs, and admission policies are in place.
- All baselines live next to infrastructure code so drift detection (`terraform plan`, `kubectl diff`) is part of the release checklist.

