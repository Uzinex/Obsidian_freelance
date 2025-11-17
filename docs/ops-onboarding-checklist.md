# Ops Onboarding Checklist

- [ ] Account setup: GitHub, Terraform Cloud, ArgoCD, Grafana, Datadog, PagerDuty.
- [ ] Review security basics: `secrets_policy.md`, `prod-security-baseline.md`, MFA enabled everywhere.
- [ ] Local environment: follow `env-setup.md`, run unit/integration tests.
- [ ] Read core run-books: `ops-handbook.md`, `release-guide.md`, `rollback_plan.md`, `dr-runbook-and-drill-report.md`.
- [ ] Shadow current on-call for one full shift, walk through alert policies.
- [ ] Dry-run database migration on staging using latest migration script; validate metrics.
- [ ] Execute test deploy to Stage via `deploy-stage` workflow, confirm health checks.
- [ ] Execute test rollback on Stage using previous tag, capture learnings.
- [ ] Trigger synthetic transaction tests (payment, chat message, dispute) and review dashboards.
- [ ] Complete knowledge check with SRE lead; document gaps and remediation plan.
