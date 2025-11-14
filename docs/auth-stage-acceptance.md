# Stage Acceptance Checklist — Auth Modernization

This Go/No-Go checklist is executed before promoting the modernized authentication stack from Stage to Production. All items must be **Go** before launch unless an explicit waiver is approved by the Security, Platform, and Product owners.

## Stage 1 — Technical Readiness

| Item | Owner | Evidence | Status (Go/No-Go) |
|------|-------|----------|-------------------|
| Backend SAST (Bandit) run is clean (no Medium/High) | Security | Latest GitHub Actions run link | ☐ Go / ☐ No-Go |
| Frontend ESLint run is clean (warnings disabled) | Frontend Lead | GitHub Actions log | ☐ Go / ☐ No-Go |
| Secret scan (Gitleaks) reports no leaks | Security | GitHub Actions log | ☐ Go / ☐ No-Go |
| OWASP ZAP baseline vs Stage reports 0 High alerts, Mediums triaged | Security | Stored report link | ☐ Go / ☐ No-Go |
| Sentry auth alerts configured and tested | Platform | Screenshot / alert test run | ☐ Go / ☐ No-Go |
| Prometheus/Grafana dashboard updated with new auth metrics | Observability | Dashboard URL | ☐ Go / ☐ No-Go |
| Dark launch flag wired (see below) | Backend | Feature flag config screenshot | ☐ Go / ☐ No-Go |

## Dark Launch Plan

- Feature flag: `auth.modern_login_enabled`
- Rollout strategy:
  1. Stage: enable for QA accounts only.
  2. Production: start with 5% of traffic, gradually expand to 50% over 48 hours.
  3. Monitor alerts listed in `docs/auth-observability-dashboard.md` and roll back if any go No-Go.
- Rollback switch: set `auth.modern_login_enabled=false` to route users back to legacy auth immediately.

## Legacy TokenAuth Sunset

- Precondition: modern authentication path stable for ≥ 7 days in Production.
- Final shutdown step: set `auth.token_legacy=false` in Production configuration management.
- Communication: notify customers 72 hours prior, update `status.obsidian.example.com`, and refresh API docs.

## Final Approval

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Security Owner | | | |
| Platform Owner | | | |
| Product Owner | | | |
