# Communications Observability & Alerts

## Цели

Покрыть чат, споры и уведомления едиными дашбордами в Prometheus/Grafana и Sentry, с порогами алёртов.

## Дашборды

### 1. Chat Health

**Datasources**: Prometheus (`chat_ws_*`), Loki, Sentry issues `chat-*`.

| Виджет | Метрика | Детали |
| --- | --- | --- |
| Latency percentiles | `histogram_quantile(0.95, sum(rate(chat_ws_delivery_latency_ms_bucket[5m])) by (le))` | p50/p95/p99, разделение по региону. |
| Connection health | `chat_ws_active_connections`, `ws_reconnect_attempts` | Dual-axis график. |
| Error rate | `rate(chat_ws_errors_total[5m])` по коду | Stack area. |
| Fallback usage | `chat_fallback_sessions_total` (ws→sse, ws→poll) | Сравниваем норму < 2%. |
| Message throughput | `rate(chat_messages_published_total[1m])` | Линия + пороги. |

### 2. Disputes SLA

| Виджет | Метрика |
| --- | --- |
| SLA countdown | `dispute_sla_remaining_seconds` (avg, min) |
| Overdue cases | `dispute_cases_overdue` (count, grouped by owner) |
| Resolution time histogram | `dispute_resolution_time_seconds_bucket` |
| Outcome distribution | PostHog cohort → embedded chart (win_client/win_freelancer/split). |
| NPS after dispute | `dispute_nps_score` rolling avg. |

### 3. Notifications

| Виджет | Метрика |
| --- | --- |
| Delivery success | `notification_delivered_total / notification_attempted_total` по каналу |
| Drop rate | `notification_dropped_total / notification_attempted_total` |
| Error table | Sentry issues с тегом `channel` + `template` |
| Queue depth | `notification_queue_depth` |
| Retry heatmap | `notification_retry_count_bucket` |

## Алерты

| Название | Условие | Канал |
| --- | --- | --- |
| `ALERT chat_ws_latency_high` | `histogram_quantile(0.95, chat_ws_delivery_latency_ms) > 1s` 5 мин | PagerDuty Sev2 |
| `ALERT chat_ws_disconnect_storm` | `ws_reconnect_attempts > 1000` за 5 мин И `chat_fallback_sessions_total > 0.1 * chat_sessions_total` | PagerDuty Sev1 |
| `ALERT dispute_overdue_breach` | `dispute_cases_overdue > 5` 10 мин | Slack #ops-disputes |
| `ALERT notification_delivery_drop` | `notification_delivered_total / notification_attempted_total < 0.99` 15 мин | Slack #notif-oncall |
| `ALERT notification_queue_backlog` | `notification_queue_depth > 5000` 10 мин | PagerDuty Sev3 |
| `Sentry: Chat Gateway WS_ERROR` | Issue rate > 10/min, auto-resolve при <2/min | PagerDuty + email |
| `Sentry: NotificationWorkerDeliveryError` | >50 events/5min | Slack |

## Интеграция

- Метрики добавляются через Prometheus exporters в сервисах `chat-gateway`, `chat-worker`, `notification-worker`, `dispute-service`.
- SLO проверки (p95 ≤ 1c, drop-rate ≤ 1%) вшиты в Grafana alerts и проходят stage валидацию.
- Dashboards версионируются в `infrastructure/observability/dashboards/communications.jsonnet`.
