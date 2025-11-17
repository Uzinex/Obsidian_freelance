# FinOps Monthly Report Template

> Owner: FinOps Lead  
> Due date: 5th business day each month

## 1. Executive summary
- Total cloud spend vs. budget
- % change MoM and YoY
- Key drivers (traffic, feature launch, anomalies)

## 2. Tag compliance snapshot
| Environment tag | Compliance % | Notes |
| --- | --- | --- |
| `env` (prod/stage/dev) |  |  |
| `service` (api/chat/payments/analytics) |  |  |
| `component` (db/cache/queue/cdn) |  |  |

## 3. Cost by service
| Service | Spend (USD) | Budget | Variance | Notes |
| --- | --- | --- | --- | --- |
| API |  |  |  |  |
| Web |  |  |  |  |
| Payments |  |  |  |  |
| Chat |  |  |  |  |
| Analytics |  |  |  |  |
| Shared Infra |  |  |  |  |

## 4. Cost per contract/payment
| Metric | Formula | Value | Trend |
| --- | --- | --- | --- |
| Cost per active contract | `Total infra spend / # active contracts` |  |  |
| Cost per processed payment | `Payments infra spend / # payments` |  |  |
| Storage cost per GB | `Object storage spend / avg GB stored` |  |  |

## 5. Budget & anomaly alerts
- Alerts triggered (AWS Budgets, GCP Billing, CloudZero, etc.)
- Root cause + remediation actions
- Forecast adjustments required?

## 6. Optimization plan
| Initiative | Owner | Est. savings | Target date | Status |
| --- | --- | --- | --- | --- |
|  |  |  |  |  |

## 7. Action items
- [ ] Confirm all new resources carry `env/service/component` tags.
- [ ] Review idle assets report (unattached EBS, low-utilization RDS, overprovisioned K8s nodes).
- [ ] Update stakeholders in the #finops channel.

