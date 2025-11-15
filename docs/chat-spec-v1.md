# Chat spec v1

This document codifies the minimum viable contract chat. It complements the escrow event map and the communications feature flag matrix.

## Message lifecycle

```
DRAFT (client side) -> SENT -> DELIVERED -> READ
```

* **SENT.** Server accepted the payload, stored the message and enqueued a `chat.message` event. `sent_at` is immutable.
* **DELIVERED.** Recipient's device acknowledges receipt (either through the WebSocket consumer or the `/messages/{id}/status/` endpoint). `delivered_at` is set once and never overwritten.
* **READ.** User opened the thread. `read_at` is set together with `delivered_at` if it was still `NULL`.
* Any moderation action (`hide`, `soft_delete`) preserves timestamps and adds `hidden_at/hidden_by`.

### State rules

1. The server enforces monotonic transitions: `READ` implies `DELIVERED`, therefore skipping directly from `SENT` to `READ` is allowed, but regressing to `SENT` is not.
2. System messages reuse the same state machine but always stay in `READ`.
3. The SSE/polling fallback (`GET /api/chat/contracts/{id}/events/`) streams both new messages and status updates in the same chronological order as the WebSocket channel.

## Attachments

| Parameter | Value |
| --- | --- |
| Max size | 15 MB after EXIF scrubbing |
| Allowed MIME types | `image/jpeg`, `image/png`, `application/pdf`, `application/zip` |
| Signature check | SHA-256 digest stored on the record; type detection relies on magic bytes |
| Antivirus | Reuses the `upload.scanner` feature flag and `uploads.scanner.scan_bytes` integration |
| Storage | Private FS (`uploads.storage.private_storage`) under `chat/attachments/{Y}/{m}/{d}` |
| Delivery | Download requires a presigned token issued by `POST /api/chat/contracts/{id}/attachments/{attachment_id}/presign/` with a TTL of 60–3600 seconds |
| Privacy | All images go through EXIF stripping before persisting |

### Attachment search helpers

`ChatMessage.contains_link` and `ChatMessage.has_attachments` drive the tag filters used by the API (`?tag=link` or `?tag=has_attachments`). These tags are the only facets exposed by the v1 search UI.

## Rate limiting and flood control

| Scope | Burst window | Default limit | Storage key |
| --- | --- | --- | --- |
| User → all chats | 1 second | 5 messages | `chat:user:{user_id}:sec` |
| User → all chats | 60 seconds | 30 messages | `chat:user:{user_id}:min` |
| Thread aggregate | 1 second | 8 messages | `chat:thread:{thread_id}:sec` |
| Thread aggregate | 60 seconds | 60 messages | `chat:thread:{thread_id}:min` |

Additional controls:

1. `ChatThread.blocked_until` lets moderators pause an entire conversation. API responses return HTTP 403 with a localized message.
2. The WebSocket consumer mirrors the same rate-limits and emits `{type:"error", code:"rate_limited"}` payloads without closing the socket.
3. Last-activity stamps are cached for 5 minutes (`chat:last:{thread_id}:{user_id}`) to detect reconnect storms. When a reconnect happens within this window we delay auto retries client-side by 500–1000 ms.

## Transport channels

1. **Primary:** `ws://<host>/ws/chat/contracts/{id}/` handled by `ContractChatConsumer`. Supports send, delivered/read acknowledgements, optional presence/typing (controlled by `chat.presence`).
2. **Fallback:** HTTP polling (`GET /api/chat/contracts/{id}/events/?since=<ISO8601>`). Returns `{events: [...], next_cursor: ...}` and is intended for mobile push workers or browsers without WebSocket support.
3. **Delivery semantics:** both channels emit the same JSON envelopes `{type: "message"|"status"|"presence"|"typing", payload: ...}` to simplify the frontend.

## Retention and storage

* Messages live in PostgreSQL for 18 months. After that a scheduled task exports them to cold storage and flags `ChatMessage.is_hidden=True` so they disappear from UI pagination.
* Attachments follow the same retention timeline but can be purged earlier if a user requests deletion. Metadata is preserved for audit purposes.
* Presigned attachment links expire automatically; the download view validates both the token and the requester’s membership in the thread.

## Operational notes

* REST API base path: `/api/chat/contracts/{contract_id}/...`.
* All endpoints require authentication. Staff/moderators bypass participant checks but every request is logged via the standard audit middleware.
* Feature flags: `chat.enabled`, `chat.attachments`, `chat.presence`.
* System actions such as “Предложить milestone”, “Запросить правки”, “Открыть спор” are rendered as quick actions in the frontend but tracked as regular messages with the `tags=["action"]` label for analytics.
