# Alert Policy and On-Call Guide

## Service Level Indicators / Objectives
| SLI | Definition | SLO |
| --- | --- | --- |
| API availability | Successful HTTP responses / total | 99.9% monthly |
| API latency | p95 < 300 ms, p99 < 500 ms | 99% of minutes |
| WebSocket latency | p95 < 1 s | 99% of minutes |
| Error rate | 5xx per minute < 1% | 99% of minutes |
| Replica lag | `now() - replay_timestamp` | < 10 s |
| Queue depth | Tasks waiting / minute | < 500 fast, < 100 heavy |
| Backup success | Completed jobs / scheduled | 100% daily |
| PSP webhook success | 2xx per attempt | > 99.5% |

SLO compliance checked via `ci/check_sli.py` script using Prometheus queries. Violations recorded in weekly ops review; 28-day rolling window.

## Alert Thresholds
- **Uptime**: Alertmanager fires when availability over 5 minutes < 99%; page L1.
- **API Latency**: Warning at p95>250 ms for 5 min; Critical at >300 ms for 2 min.
- **WebSocket Latency**: Critical if p95>1s for 5 min.
- **5xx Rate**: Warning >0.5%, Critical >1% for 3 consecutive minutes.
- **Celery Queue Length**: Warning fast queue >300 for 5 min; Critical >500. Heavy queue warning >60, critical >100.
- **Replica Lag**: Warning >5s, Critical >15s.
- **Backups**: Page if no success metric `backup.success=1` in past 26h.
- **Redis Memory/Evictions**: Warning at 70% usage, Critical at 85% or any eviction event.
- **PSP Webhooks**: Critical if error rate >2% or 3 consecutive failures per PSP.

## Alert Routing & Escalation
1. **L1 SRE On-call** (primary): receives PagerDuty/Telegram push. Acknowledges within 5 min.
2. **L2**: Domain experts
   - Backend guild
   - Frontend guild
   - DevOps/Infra owner
3. **L3**: Finance (escrow/payout), Moderation (content), Compliance for PSP incidents.
4. Notification channels: PagerDuty → Telegram bridge, Slack #alerts, fallback email.
5. If L1 no response in 10 min, auto escalate to L2. Another 10 min to escalate to L3 + leadership.

## Runbooks Referenced
- Database: `docs/db-runbook.md`
- Queues/DLQ: `docs/queues-and-retries-matrix.md`
- CDN/Object storage: `docs/object-storage-and-cdn-policy.md`

## On-Call Expectations
- Carry laptop + VPN token.
- Perform daily log review (structured JSON via Loki) for anomalies.
- File incident report within 24h for Sev1/Sev2.

## Noise Control
- Sentry filters bot user agents and known 4xx noise; include `environment`, `user_segment`, `feature_flag` tags for triage.
- Rate-limit repeating alerts with Alertmanager inhibition rules (e.g., degrade noise when parent outage alert firing).

## Pager Testing
- Weekly synthetic alert injection using `./scripts/fire_test_alert.sh --service api --severity warning`.
- Ensure contact methods updated before each rotation.

## Communication Template
```
[ALERT] <Service> <Severity>
Start: <UTC timestamp>
Impact: describe
Mitigation: link to PR/runbook
Next update: +15 min
```
