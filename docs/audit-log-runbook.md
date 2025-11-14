# Audit Log Runbook

This document explains how authentication and security events are captured in
`accounts.models.AuditEvent` and how to investigate incidents by correlating
application logs with tracing systems such as Sentry.

## Event schema overview

Audit events are written through `accounts.audit.audit_logger`. The service
collects request metadata (IP address, user agent, HTTP method and path) and
links each entry to distributed tracing headers when present.

| Field | Description |
| --- | --- |
| `event_type` | Categorical value describing the action (login, 2FA toggle, KYC view, access denial, etc.). |
| `user` | Actor who triggered the event. May be `NULL` for anonymous access denials. |
| `session` | Related `AuthSession` when available. Useful for correlating refreshes and revocations. |
| `trace_id` / `span_id` | Extracted from `sentry-trace`, `traceparent`, `X-Trace-Id`, or `X-Request-Id` headers. Use these identifiers to jump to full request traces in Sentry or your tracing backend. |
| `metadata` | JSON payload with contextual attributes (target profile, document ID, response body for denials, etc.). |
| `status_code` | HTTP status code for access-denied responses. |
| `created_at` | When the event was recorded. |

### Event catalogue

| Event type | When it fires |
| --- | --- |
| `login`, `refresh`, `logout`, `logout_all` | Session lifecycle events. |
| `password_reset_request`, `password_reset_confirm` | Password reset initiation and confirmation. |
| `email_verify_request`, `email_verify_confirm`, `email_change_request`, `email_change_confirm` | Email lifecycle operations. |
| `2fa_enabled`, `2fa_disabled` | Two-factor setup, backup code regeneration, and disablement. |
| `kyc_upload`, `kyc_view` | Uploading or accessing sensitive KYC documents. |
| `role_change` | Administrative or self-service changes to a profile role. |
| `access_denied` | HTTP 401/403 responses on sensitive endpoints (API under `/api/accounts/` and `/api/uploads/`). |

## Accessing audit events

### Django shell query

```python
from accounts.models import AuditEvent
recent = AuditEvent.objects.filter(event_type="access_denied").order_by("-created_at")[:20]
for event in recent:
    print(event.created_at, event.event_type, event.user_id, event.metadata)
```

### SQL (PostgreSQL)

```sql
SELECT created_at, event_type, user_id, metadata
FROM accounts_auditevent
WHERE event_type = 'kyc_view'
  AND metadata ->> 'document_id' = '...'
ORDER BY created_at DESC;
```

### Correlating with tracing tools

1. Obtain the `trace_id`/`span_id` from the audit row.
2. Search for the same trace in Sentry or your tracing backend. For Sentry the
   search query is typically `trace:<trace_id>`.
3. Review the full request to understand upstream/downstream calls that
   occurred alongside the audited action.

If tracing is unavailable the audit metadata still captures IP, path, and
status code information for manual investigation.

## Incident investigation example

**Scenario:** A customer complains about repeated 403 responses when trying to
upload KYC documents.

1. Query audit logs for `event_type = 'access_denied'` with the customer's user
   ID.
2. Inspect the `metadata['detail']` payload to confirm the rejection reason and
   the path that was accessed.
3. Use the `trace_id` to retrieve the correlated application trace in Sentry to
   see whether RBAC, throttling, or downstream storage errors were raised.
4. Review adjacent `kyc_upload` events to verify whether the same session had
   successful uploads, noting the `session` and `device_id` fields.
5. Document findings, including whether the denial was expected (e.g. rate
   limit) or requires remediation.

## Maintenance tips

- Keep `AUDIT_SENSITIVE_PATH_PREFIXES` in `obsidian_backend.settings` aligned
  with newly introduced sensitive endpoints.
- When adding new security-sensitive flows, emit an audit event via
  `audit_logger.log_event` so investigators have a consistent data trail.
- Periodically export audit logs to a long-term retention system that meets
  your compliance requirements.
