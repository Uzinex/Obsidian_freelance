# Auth Rollout Report — Template

Use this template to document the outcome of each production rollout wave for the modernized authentication stack.

## Metadata
- **Release Window:** <!-- e.g., 2025-02-20 02:00-04:00 UTC -->
- **Change Owner:**
- **On-call Engineer:**
- **Feature Flag State (`auth.modern_login_enabled`):** <!-- % of users enabled -->
- **Legacy Flag State (`auth.token_legacy`):** <!-- true/false -->

## Pre-Deployment Checklist
- [ ] Stage acceptance checklist signed (link to `docs/auth-stage-acceptance.md` record)
- [ ] Communication sent to stakeholders (customers, support, sales)
- [ ] Rollback plan reviewed and on-call acknowledged
- [ ] Monitoring dashboards bookmarked (`docs/auth-observability-dashboard.md`)

## Deployment Timeline
| Time (UTC) | Action | Owner |
|-----------|--------|-------|
| | | |

## Observability Snapshots
- **Sentry:** <!-- attach key charts or issue list -->
- **Prometheus/Grafana:** <!-- include screenshots/links for metrics: p95 latency, failed login share, password reset rate, 2FA enrollments -->
- **Other Monitoring:** <!-- e.g., WAF, CDN -->

## Incident Log
| Time (UTC) | Severity | Description | Resolution |
|-----------|----------|-------------|------------|
| | | | |

## Post-Deployment Validation
- [ ] Login, logout, password reset, 2FA flows verified manually
- [ ] No High/Medium findings in last OWASP ZAP baseline scan
- [ ] No auth alert thresholds breached during window
- [ ] Support queue reviewed (no auth regression reports)

## Final State
- **Users migrated to modern auth (%):**
- **Legacy TokenAuth disabled:** <!-- yes/no -->
- **Open follow-up tasks:** <!-- link to Jira/Trello -->

## Sign-off
| Role | Name | Signature | Date |
|------|------|-----------|------|
| Security Owner | | | |
| Platform Owner | | | |
| Product Owner | | | |
