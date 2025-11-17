# Tracing Map – Key Flows

## Login
1. `frontend.login` span wraps credential form submission; includes `rum.session_id` attribute.
2. Backend `api.login` span records password hashing + token issuance.
3. `sso.audit` span logs security webhooks.

## Escrow Lifecycle
- **Create**: `marketplace.create_order` → `payments.authorize_hold` → `ledger.append` spans.
- **Hold**: `escrow.hold_refresh` span triggered by Celery beat; attaches PSP transaction ID.
- **Release**: `escrow.release` span includes DB transaction ID and outgoing payout request.
- **Refund**: `escrow.refund` span records rollback path with `reason` attribute.

## Chat Flow (send → deliver → read)
1. `chat.api.send` span includes message length, attachments count, user_id (hashed).
2. `chat.ws.deliver` span executed via Channels; references Redis pub/sub ID.
3. `chat.read_receipt` span triggered when user opens message; includes latency metric linking to WebSocket event.

## Payout
- `finance.payout_request` span covering PSP API call.
- `finance.payout_webhook` span handles PSP callbacks; correlates to request span via `payment_id` attribute.

## Trace Context Propagation
- Use W3C Trace Context headers from frontend to backend to Celery (stored in task headers `traceparent`, `tracestate`).
- Celery worker instrumentation automatically creates child spans when `traceparent` header present.

## Instrumentation Coverage Targets
| Flow | Required Attributes |
| --- | --- |
| Login | `user_type`, `auth_method`, `mfa_enabled`, `result` |
| Escrow | `order_id`, `psp`, `amount`, `currency`, `state` |
| Chat | `thread_id`, `message_id`, `media_present`, `delivery_status` |
| Payout | `payout_id`, `psp_batch_id`, `attempt` |

## Sampling Strategy
- Base sample rate 20%. Escrow + payouts raise sampling to 100% via `TraceIdRatioBased` + span attribute filter.

## Storage and Dashboards
- OTLP traces exported to Tempo; Grafana “Key Flows” board uses `service.name=obsidian-backend` and `flow=<flow>` tag.

## Rollout Notes
- Feature flag `tracing.otel.enabled` controls instrumentation.
- All spans include `feature_flags` attribute listing toggles affecting the request.
