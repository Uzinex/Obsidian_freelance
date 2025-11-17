# Queues, Workers, and Retry Policy

## Worker Roles
- **Fast-path worker** (`celery -Q fast -c 20`): small CPU-bound tasks (notifications fan-out, metrics updates). SLA < 2s.
- **Heavy worker** (`celery -Q heavy -c 4 --prefetch-multiplier=1`): long DB or network tasks (escrow settlement, payouts).
- **Beat scheduler**: runs cron-like tasks (`beat` queue) and publishes to target queue.
- **Dedicated media worker**: handles thumbnail/object processing, isolated due to GPU/lib dependencies.

Redis persistence:
- `appendonly yes` with `everysec`; background `bgsave` every 15 minutes. Only idempotent job metadata stored (task args, dedupe keys). Business state kept in Postgres, so Redis rebuild is acceptable.

## Retry and DLQ Strategy
- Use Celery retry policies with exponential backoff and jitter. All tasks idempotent via unique business keys (invoice_id, chat_message_id) + DB UPSERT/`SELECT ... FOR UPDATE` guards.
- After max retries tasks land in Dead Letter Queue (`dlq`) for manual handling.
- Poison messages tagged with `task_id`, `exception`, `payload_hash` and triaged via runbook below.

## Queues Matrix
| Queue | Worker Type | Concurrency | Visibility Timeout | Retries | Backoff | SLA | DLQ Action |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `fast_default` | Fast | 20 | 30s | 3 | 2^n * 5s | <2s p95 | Auto reroute to `dlq_fast` |
| `notifications_email` | Fast | 10 | 60s | 5 | 2^n * 10s | <5s p95 | Contact comms team, inspect template errors |
| `chat_events` | Fast | 15 | 15s | 2 | 2^n * 3s | <1s p95 | Replay after fixing upstream message |
| `heavy_settlements` | Heavy | 4 | 10m | 5 | 2^n * 60s | <60s p95 | Manual replay via `python manage.py replay_task <id>` |
| `heavy_payouts` | Heavy | 4 | 15m | 6 | 2^n * 90s | <120s p95 | Escalate to finance, sync with PSP |
| `media_processing` | Media | 6 | 5m | 4 | 2^n * 30s | <45s p95 | Verify object exists in S3, then replay |
| `beat` | Beat | 1 | 5m | n/a | n/a | n/a | n/a |
| `dlq_fast` | Ops | manual | n/a | n/a | n/a | n/a | Process per DLQ SOP |
| `dlq_heavy` | Ops | manual | n/a | n/a | n/a | n/a | Process per DLQ SOP |

## DLQ Operations
1. Connect to Redis `dlq_*` streams via `scripts/dlq_dump.py`.
2. For each entry capture: `task_name`, `args`, `kwargs`, `exception`, `retries`.
3. Determine bucket:
   - **Bug** → create Jira, leave task in DLQ.
   - **Transient** → fix upstream dependency, then `celery control retry <task_id>` or copy payload into `scripts/requeue_task.py`.
4. Update DLQ incident log with timestamp, root cause, fix status.

## Idempotency Guardrails
- Every Celery task stores a dedupe key in Redis (`SET key value NX PX=86400000`).
- Heavy financial tasks additionally check Postgres `processing_log` table with `(task_name, business_id)` unique constraint.
- Tasks mutate state using transactions; rollbacks ensure safe retries.

## Retry Policy Reference
```python
@app.task(bind=True, autoretry_for=(RequestException,), retry_backoff=5, retry_backoff_max=300,
          retry_jitter=True, max_retries=5)
def send_webhook(self, payload):
    with metrics.histogram('webhook.latency').time():
        return webhook_client.send(payload)
```

## Operator Commands
- Inspect queues: `celery -A obsidian_backend inspect active --destination=worker@host`
- Purge DLQ: `redis-cli -n 4 DEL dlq_fast`
- Replay DLQ message: `python manage.py replay_task <task_id> --queue fast_default`
