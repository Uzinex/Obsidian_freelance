# Authentication Audit Events

All sensitive authentication actions emit structured audit records stored in `accounts.AuditEvent`. The table enables security teams to trace activity across sessions without storing sensitive payloads.

## Model fields

| Field | Type | Description |
| --- | --- | --- |
| `id` | bigint (auto) | Primary key. |
| `user` | FK to `accounts.User` | Owner of the event. |
| `session` | FK to `accounts.AuthSession` (nullable) | Session associated with the action when available. |
| `device_id` | `CharField(128)` | Device identifier supplied by the client ("*" for bulk actions). |
| `event_type` | `CharField(32)` | One of: `login`, `logout`, `logout_all`, `refresh`, `2fa_enabled`, `2fa_disabled`, `password_reset_request`, `password_reset_confirm`, `email_verify_request`, `email_verify_confirm`, `email_change_request`, `email_change_confirm`. |
| `ip_address` | `GenericIPAddressField` | Source IP (nullable). |
| `user_agent` | `TextField` | Client user-agent string when available. |
| `metadata` | `JSONField` | Optional structured context (e.g., `{ "used_backup_code": true }`). |
| `created_at` | `DateTimeField` | Timestamp of the event. |

## Event triggers

| Event | Trigger |
| --- | --- |
| `login` | Successful `/api/auth/login/`. |
| `logout` | `/api/auth/logout/` (single session). |
| `logout_all` | `/api/auth/logout-all/` revoking every session. |
| `refresh` | `/api/auth/refresh/` issuing new tokens. |
| `2fa_enabled` | Successful 2FA enablement or backup code regeneration. |
| `2fa_disabled` | 2FA disabled for the account. |
| `password_reset_request` | `/api/auth/password/reset/request/`. |
| `password_reset_confirm` | `/api/auth/password/reset/confirm/`. |
| `email_verify_request` | `/api/auth/email/verify/request/`. |
| `email_verify_confirm` | `/api/auth/email/verify/confirm/`. |
| `email_change_request` | `/api/auth/email/change/request/`. |
| `email_change_confirm` | `/api/auth/email/change/confirm/`. |

## Usage guidelines

- Audit data should be exported to the central logging pipeline or SIEM in production.
- Metadata keys must exclude PII beyond device identifiers and coarse-grained flags.
- For long-term retention, rotate logs according to the organisation's compliance requirements.
