# Synthetics and RUM Dashboard Spec

## Synthetic Journeys
- **Scenario**: Landing → Login → Post order → Hold funds → Chat message.
- Tooling: k6 browser or Playwright cron job triggered via GitHub Actions every 5 minutes per region (eu-central-1, ap-south-1).
- Credentials stored in Vault dynamic secrets; rotate weekly.
- Steps tracked with custom metrics (`synthetic_step_latency_seconds{step="login"}`).
- Failure criteria: any step > 3s or HTTP status >=500 triggers PagerDuty warning.
- After scenario completes, call `/api/self-check` to verify dependencies (DB, Redis, PSP sandbox).

## RUM Collection
- Web SDK collects Web Vitals (LCP, CLS, INP) and custom spans.
- Dimensions: locale (`uz`, `ru`), device (`mobile`, `desktop`), network (`4g`, `wifi`, `slow-3g`).
- Sampling: 5% for anonymous users, 20% for authenticated.
- Data sent to Grafana Faro → Loki/Tempo for correlation.

## Dashboard Layout
1. **Overview**
   - Status of last synthetic run per region with SLA badge.
   - Error budget burn-down for API and WS.
2. **Synthetic Steps**
   - Timeseries for each scenario step (p50/p95), stacked diff between regions.
   - Table of recent failures with screenshot links.
3. **RUM Web Vitals**
   - Heatmap of LCP per locale/device.
   - Bar chart of CLS percentile distribution.
   - INP trend line with release annotations.
4. **Correlations**
   - Scatter plot (LCP vs API latency) using shared trace IDs.
   - Overlay of feature flags toggled during spikes.
5. **Alerts**
   - Synthetic failure ratio >5% over 30 min.
   - RUM LCP p75 > 2.5s for any locale for 10 min.

## Data Retention
- Synthetic results kept 30 days for trend analysis.
- RUM metrics aggregated hourly and stored 90 days.

## Ownership
- Web Platform team maintains dashboards; SRE ensures collectors running.
- Any spec changes require PR in `docs/synthetics-and-rum-dashboard-spec.md` with approvals from both teams.
