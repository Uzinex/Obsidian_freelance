# Communications Analytics & Events

Документ описывает ключевые продуктовые и технические метрики коммуникационного стека (чат, уведомления, споры) и схему событий для текущей системы аналитики PostHog с экспортом в GA4.

## Продуктовые метрики

| Метрика | Описание | Источники данных | Целевое значение | Визуализация |
| --- | --- | --- | --- | --- |
| Доля контактов | Доля контрактов, внутри которых было хотя бы одно сообщение в чате (`contracts_with_messages / active_contracts`). | `contract_started`, `chat_message_sent` | ≥ 95% активных контрактов | Линейный график по неделям.
| Конверсия «чат → контракт» | Пользователи, начавшие переписку в чатах откликов и дошедшие до создания контракта (`contracts_started_from_chat / chats_with_proposal`). | `chat_thread_created`, `contract_started` | ≥ 35% | Воронка (чат → обсуждение условий → контракт).
| Среднее время ответа | Средний `first_reply_latency_sec` между получением и ответом по контракту. | `chat_message_received` + `chat_message_replied` | p50 ≤ 2 мин, p95 ≤ 10 мин | Percentile chart (p50/p95).
| Доля споров по контрактам | `contracts_in_dispute / total_closed_contracts`. | `dispute_opened`, `contract_closed` | ≤ 7% | Area chart.
| Исходы споров | Распределение статусов `dispute_resolved` (win_client / win_freelancer / split / cancelled). | `dispute_resolved` | - | Pie/stacked bar.
| NPS после закрытия спора | Средний NPS опроса, отправленного после `dispute_resolved`. | `dispute_nps_submitted` | ≥ +35 | KPI tile.

## Технические метрики

| Метрика | Описание | Источник/инструмент | Цель |
| --- | --- | --- | --- |
| p95/p99 задержки WS-событий | `latency_ms` между отправкой сервером и доставкой клиенту. | WebSocket telemetry + Prometheus histogram `chat_ws_delivery_latency_ms`. | p95 ≤ 1000 мс, p99 ≤ 2000 мс. |
| Ошибки доставки | Количество/доля событий `notification_delivery_failed` по каналам (e-mail, web push). | Worker logs → Sentry tag `channel`. | ≤ 0.5% в сутки. |
| Drop-rate e-mail/web push | Доля не доставленных из-за блокировок/отписок. | ESP вебхуки + PostHog event `notification_dropped`. | ≤ 1%. |
| Backoff WS переподключений | Среднее число попыток до стабильного подключения. | Metric `ws_reconnect_attempts` | ≤ 3.

## Схема событий (PostHog → GA4)

| Событие | Назначение | Основные свойства | Триггер |
| --- | --- | --- | --- |
| `chat_thread_created` | Создание нового чата (по заказу, контракту или спору). | `thread_type`, `contract_id`, `participants_count`, `initiator_role`. | После успешного ответа API создания чата (backend отправляет в PostHog, фронт — в GA4). |
| `chat_message_sent` | Отправка сообщения пользователем. | `message_id`, `thread_id`, `sender_role`, `has_attachment`, `message_kind` (text/system/file), `first_response` (bool). | После подтверждения сохранения сообщения в БД.
| `chat_message_delivered` | Доставка сообщения на все подписанные клиенты. | `message_id`, `delivery_latency_ms`, `delivery_channel` (ws/sse/poll). | Сервис доставки.
| `chat_message_failed` | Ошибка отправки/модерации. | `message_id`, `failure_code`, `moderation_reason`. | Валидация/модерация.
| `chat_thread_archived` | Архивирование после закрытия контракта. | `contract_id`, `reason`. | Постобработка контракта.
| `dispute_opened` | Старт спора по контракту. | `dispute_id`, `contract_id`, `initiator_role`, `reason_category`. | Сервис споров.
| `dispute_state_updated` | Изменение статуса спора. | `dispute_id`, `state`, `sla_remaining_sec`. | При каждом переходе.
| `dispute_resolved` | Финализация. | `resolution`, `payout_split`, `resolution_time_sec`. | Закрытие спора.
| `dispute_nps_submitted` | NPS после закрытия. | `score`, `role`, `comment_length`. | Опросная форма.
| `notification_delivery_scheduled` | Создание задания на доставку уведомления. | `notification_id`, `channel`, `template`. | Notification service.
| `notification_delivery_failed` | Неуспешная попытка. | `notification_id`, `channel`, `error_code`, `retry_count`. | Worker.
| `notification_dropped` | Отказ от отправки (отписка, throttling). | `notification_id`, `channel`, `drop_reason`. | Notification service.
| `ws_connection_opened` | Подключение клиента к WS. | `client_id`, `connection_region`, `protocol_version`. | Gateway.
| `ws_connection_closed` | Закрытие соединения. | `client_id`, `close_code`, `uptime_sec`, `fallback_used`. | Gateway.

### Интеграция

- **PostHog** — основной сборщик. Все события идут через backend SDK с единым middleware для нормализации `distinct_id` и контракта.
- **GA4** — получает агрегированное подмножество: `chat_thread_created`, `chat_message_sent`, `contract_started`, `dispute_opened`, `dispute_resolved`, `notification_delivery_failed`. Маппинг выполняется через PostHog exporter (раз в 5 мин). Названия параметров соответствуют GA4 (`thread_type`, `sender_role`).
- **Антидубляж** — idempotency key = `event_name:event_id` (message_id, dispute_id, notification_id).
- **PII** — свойства, содержащие чувствительные данные, предварительно хэшируются (ID контрактов оставляем, содержимое сообщений не логируем).

## Использование метрик

1. **Доля контактов / Конверсия «чат → контракт»** — рассчитываются ежедневными агрегатами в ClickHouse; отчёты в PostHog dashboards и экспорт в BI.
2. **Среднее время ответа** — вычисляется на лету при записи `chat_message_sent` с признаком `first_response`. Хранится как отдельная time-series метрика для SLA.
3. **Доля споров / Исходы** — формируются из `dispute_state_updated` и `contract_closed`. Используются для дашборда Dispute SLA.
4. **NPS после спора** — survey tool шлёт `dispute_nps_submitted` → PostHog → таблица `communications_nps`. На уровне продукта — cohort analysis по инициатору.
5. **p95/p99 WS** — Prometheus histogram, алерт при превышении (см. документ об наблюдаемости).
6. **Ошибки доставки / Drop-rate** — PostHog → daily ratio + Sentry issues по каналам.

## Требования к реализации

- Все события отправляются в асинхронный ingestion-воркер, который гарантирует доставку в PostHog и батчевый экспорт в GA4.
- Фронтенд при деградации отправляет события напрямую в GA4 (fallback) и повторяет в PostHog при восстановлении (по `localStorage queue`).
- Каждое событие содержит `contract_id` или `thread_id` для сквозной аналитики.
- Для споров — добавляем `sla_bucket` ("<24h", "24-48h", "48h+") для мониторинга просрочек.
