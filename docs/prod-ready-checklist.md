# Prod Ready Checklist

## Infra / Network
- [ ] Multi-AZ Kubernetes clusters healthy; cluster-autoscaler tested under load.
- [ ] Ingress controllers have WAF + rate limiting rules deployed.
- [ ] Network policies restrict east-west traffic to approved namespaces.
- [ ] Global CDN + fallback POP validated via failover drill.

## CI/CD & Deploy
- [ ] Main branch protected with required reviews and green CI.
- [ ] Deploy pipeline has manual approval + automated smoke tests.
- [ ] Rollback workflow validated in staging within last 30 days.
- [ ] Feature flags / canary routing defined for new capabilities.

## DB / Redis / S3
- [ ] Primary & replica lag dashboards <100 ms; alerts firing in staging test.
- [ ] Backup + restore drill completed in last quarter (see `db-restore-guide.md`).
- [ ] Redis persistence snapshot schedule verified; eviction policies documented.
- [ ] S3 buckets encrypted (SSE-KMS) and lifecycle policies prune PII.

## Observability
- [ ] Golden signals dashboards for BE, FE, Payments live with SLO overlays.
- [ ] Alert policy reviewed; paging rotation updated in PagerDuty.
- [ ] Trace sampling covers payments, chat, disputes critical paths.
- [ ] Synthetic monitors for payment, chat, dispute, payout flows green.

## Security & Privacy
- [ ] Secrets rotated per policy; secret scanning enforced in CI.
- [ ] MFA + hardware keys required for prod access.
- [ ] Data classification applied to new tables/events; privacy review signed off.
- [ ] Vulnerability scan (SCA + container) has no critical issues open.

## DR & Backups
- [ ] DR runbook executed and RTO/RPO met in last 6 months.
- [ ] Cross-region replicas for DB/Redis validated via failover test.
- [ ] Backups stored off-site with immutability window configured.
- [ ] Incident communication templates up to date.

## FinOps
- [ ] Cost dashboards reviewed; anomaly alerts configured (<10% over baseline).
- [ ] Reserved/spot capacity plan documented for compute + DB.
- [ ] Feature flag toggles include cost estimate for steady state.
- [ ] Rollout report captures incremental cloud spend.

## Docs & Onboarding
- [ ] Ops handbook + run-books reviewed and versioned.
- [ ] Onboarding checklist completed for every on-call engineer.
- [ ] Stage→Prod acceptance protocol filled for current release.
- [ ] Post-rollout report stored with links to evidence.
