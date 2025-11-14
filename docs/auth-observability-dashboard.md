# Auth Observability Dashboard & Alerting

This guide documents the observability and alerting setup for authentication flows. It covers Sentry instrumentation, alert rules for HTTP anomalies, and Prometheus/Grafana dashboards for deeper performance metrics.

## Sentry Configuration

1. **Tagging and Filtering**
   - Add the tag `feature:auth` to every request handler that services `/auth/**` routes (login, logout, password reset, 2FA, token refresh).
   - Use `scope.set_tag("auth.route", request.path)` (Python) or `Sentry.setTag("auth.route", route)` (frontend) during request handling so errors can be grouped by endpoint.
   - For background jobs (e.g., password reset emails), add `scope.set_tag("auth.flow", "password-reset")` to link exceptions to the auth feature set.
   - Configure Sentry inbound filters to drop noise:
     - Ignore client-side script errors unrelated to auth by filtering events without `feature:auth`.
     - Filter known bot traffic by excluding user agents that match `(?i)bot|spider|crawl`.

2. **Dashboards**
   - Create a Sentry dashboard named **“Auth Reliability”** containing:
     - Error count by `auth.route` (stacked bar, 24h window).
     - Issues by severity filtered with `feature:auth`.
     - Apdex for requests tagged `feature:auth`.

## Alert Rules

Configure the following alerts in Sentry (or equivalent incident system). Each alert should auto-page the on-call engineer and post to the `#auth-alerts` Slack channel.

| Alert | Trigger | Threshold | Notes |
|-------|---------|-----------|-------|
| **Unauthorized Spike** | Aggregation of `HTTP 401` + `HTTP 403` events tagged with `feature:auth` | 5-minute rolling count ≥ **50** and 300% over 7-day baseline | Indicates auth failures or misconfigurations. Include recent deploy SHA in notification. |
| **Login Throttling Spike** | `HTTP 429` events on `auth.route` = `/auth/login` | ≥ **20** events over 5 minutes | Signals abuse or throttling misconfiguration. |
| **Auth Service 5xx** | `HTTP 5xx` errors tagged `feature:auth` | ≥ **5** events in 5 minutes OR ≥ **1** event for severity `fatal` | Escalate immediately; attach recent logs. |

## Prometheus & Grafana Metrics

For services that export Prometheus metrics, instrument the following and surface them on a Grafana dashboard named **“Auth Experience”**:

| Metric | Description | PromQL Example | Grafana Panel |
|--------|-------------|----------------|---------------|
| `auth_login_latency_seconds` | Histogram timer for login attempts. | `histogram_quantile(0.95, sum(rate(auth_login_latency_seconds_bucket[5m])) by (le))` | **p95 Login Latency** (line chart). |
| `auth_login_attempts_total{status}` | Counter labelled by `status="success"|"failure"`. | `sum(rate(auth_login_attempts_total{status="failure"}[5m])) / sum(rate(auth_login_attempts_total[5m]))` | **Failed Login Share** (percentage stat). |
| `auth_password_reset_requests_total` | Counter incremented per password reset initiation. | `sum(rate(auth_password_reset_requests_total[1h]))` | **Password Reset Rate** (bar per hour). |
| `auth_two_factor_enroll_total` | Counter for 2FA enablement events. | `sum(rate(auth_two_factor_enroll_total[1d]))` | **2FA Enrollments** (daily table). |

### Alerting from Prometheus/Grafana

Set alert rules in Alertmanager (or Grafana Alerting) for:
- **p95 Login Latency Degradation**: `histogram_quantile(0.95, sum(rate(auth_login_latency_seconds_bucket[5m])) by (le)) > 2` seconds for 10 minutes.
- **Failed Login Ratio Spike**: Failed login share > 25% over 10 minutes.
- **Password Reset Surge**: Password reset rate > baseline × 3 over 30 minutes.
- **2FA Enrollment Drop**: 2FA enrollment rate < 5 per day for 48 hours (signals broken flows).

Each alert should page on-call and open a Jira incident with runbook link `docs/auth-audit-events.md` for context.
