# Prod Rollout Report Template

## Summary
- Release ID / Tag:
- Date & Time of Full Rollout:
- Traffic Allocation Path (10% → 20% → 100%):
- Participants: BE / FE / Payments / SRE / Support / Product.

## Timeline
| Time (UTC) | Event | Owner | Notes |
| --- | --- | --- | --- |
|  | Canary start (10%) |  |  |
|  | Canary expand (20%) |  |  |
|  | Full rollout (100%) |  |  |

## Health Metrics
- Error rate vs SLO:
- Latency p95 vs baseline:
- Payments success rate:
- Chat delivery rate:
- Dispute SLA impact:
- Payout settlement latency:

## Issues & Mitigations
| ID | Description | Impact | Mitigation | Follow-up Owner |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

## Post-Deployment Validation
- [ ] Control scenarios executed with evidence links.
- [ ] Logs / traces reviewed; anomalies noted.
- [ ] Support confirms no spike in tickets.
- [ ] Cost impact analyzed (FinOps).

## Decision & Next Steps
- ✅ Rollout steady-state confirmed / ❌ rollback executed.
- Action items & due dates.

## Domain Owners
- Backend: @be-lead (backup @be-oncall)
- Frontend: @fe-lead (backup @fe-oncall)
- Payments: @payments-lead (backup @payments-oncall)
- SRE: @sre-lead (backup @sre-oncall)
- Support: @support-manager (backup @support-lead)
