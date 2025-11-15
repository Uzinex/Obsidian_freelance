# Chat ↔ Escrow event map

This appendix documents how escrow lifecycle changes are surfaced in the contract chat as system messages. Every event is appended to the corresponding `ChatThread` with `sender=None`, `is_hidden=False`, `has_attachments=False` and `tags=["system"]` so it is rendered distinctly from participant authored messages.

| Escrow event | Trigger source | Chat system message template | Additional metadata |
| --- | --- | --- | --- |
| `hold_placed` | Client funds a milestone or the escrow wallet captures an upfront deposit. | `Система: Бюджет в размере {amount} {currency} зарезервирован в эскроу для этого контракта.` | Include `amount`, `currency`, `milestone_id` if applicable. Message is posted immediately after the escrow API confirms the hold. |
| `hold_released_partial` | Finance service approves a partial release (e.g. milestone payout). | `Система: {amount} {currency} выплачено исполнителю по частичному релизу.` | Provide `amount`, `currency`, `milestone_label`. Attach a machine readable payload to the message metadata so the frontend can render a CTA that opens the milestone breakdown. |
| `hold_released_full` | Final escrow settlement when the contract is marked as complete. | `Система: Эскроу закрыт. {amount} {currency} отправлено исполнителю.` | Include `amount`, `currency`, `payout_reference`. The message is emitted even if the final release happens automatically (timeout). |
| `refund_requested` | Client opens a dispute or requests a refund before payout. | `Система: Клиент запросил возврат средств. Статус контракта — спор.` | Add `dispute_id` and a `cta` flag so the UI can deep-link to the dispute flow. |
| `refund_processed` | Operations team confirms a refund. | `Система: Возврат на сумму {amount} {currency} отправлен клиенту.` | Include `amount`, `currency`, `refund_reference` and whether the freelancer has been notified separately. |
| `escrow_hold` | Automatic alert whenever escrow is paused because of AML, chargeback or compliance checks. | `Система: Эскроу временно заблокирован до завершения проверки. Отправка средств приостановлена.` | Provide `reason_code` and `expected_review_at` so support can communicate realistic timelines. |

## Posting rules

1. **Ordering.** System messages reuse the same timestamp fields as regular chat messages. They participate in pagination and HTTP/WebSocket event streams to guarantee chronological fidelity.
2. **Idempotency.** Each escrow event is written with a stable `idempotency_key` derived from the escrow record to avoid duplicates on retries.
3. **Localization.** Templates are stored as translation keys (`chat.system.escrow.hold_placed`, etc.) to support future localization work.
4. **Audit trail.** Every system message includes `metadata` with the raw escrow payload. This metadata is stored in the private audit log bucket for compliance reviews but is not exposed to the client.
