# Prod Acceptance Protocol Template

## Release Overview
- Release ID / Tag:
- Change Summary:
- Owners: BE / FE / Payments / SRE / Support
- Date Range for Dark Launch:

## Stage → Prod Procedure
1. **Dark Launch**: enable feature for 10–20% prod traffic via flag `<feature_flag>`.
2. **Observation Window**: monitor for 7 days; track latency, error budget consumption, business KPIs.
3. **Control Scenarios** (run on prod immediately after dark launch and after observation window):
   - Payment happy path (card + wallet).
   - Chat initiation and media upload.
   - Dispute creation and status update.
   - Payout request and settlement.
4. **Rollback Plan**: link to `rollback_plan.md` and confirm tested in stage.
5. **Sign-offs**: BE, FE, Payments, SRE, Support, Product, Compliance.

## Evidence Checklist
- [ ] Canary metrics screenshots / links.
- [ ] Logs / traces sampled for critical flows.
- [ ] Incident review (if any) with resolution.
- [ ] Customer communications draft prepared.

## Decision
- ✅ Promote to 100% traffic on (date/time)
- ❌ Blocker found (describe & action items)

## Domain Owners
- Backend: @be-lead (backup @be-oncall)
- Frontend: @fe-lead (backup @fe-oncall)
- Payments: @payments-lead (backup @payments-oncall)
- SRE: @sre-lead (backup @sre-oncall)
- Support: @support-manager (backup @support-lead)
