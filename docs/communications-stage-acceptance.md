# Communications Stage Go/No-Go Checklist

Используется командой релиза перед включением коммуникационного стека на Stage и перед прод-роллаутом.

## Подготовка

- [ ] Обновлены feature flags согласно `communications-feature-flags.md` (dark launch, dispute tools, exports).
- [ ] Stage окружение синхронизировано с прод данными (анонимизированный дамп ≤ 7 дней).
- [ ] Нагрузочный тест `loadtest-chat.yml` выполнен и протокол размещён (см. `chat-loadtest-and-performance.md`).

## Функциональные проверки (Go/No-Go)

| Блок | Критерии |
| --- | --- |
| Чат | Сообщения через WS/SSE/poll доставляются; read receipts и вложения работают; fallback срабатывает ≤3 сек. |
| Модерация | Автофильтр и ручная эскалация; логи аудита заполнены. |
| Споры | Открытие, переходы статусов, SLA таймеры, исходы и частичный релиз работают. |
| Нотификации | Email и web push доставляются, drop-rate <1%, deduplication подтверждена. |
| SLA/Перф | p95 latency ≤1 сек (см. дашборд Chat Health); нет просроченных споров. |
| Экспорт | Экспорт переписки доступен, пакет соответствует структуре (README, CSV, attachments, metadata). |
| Run-books | Дежурный ознакомлен с `audit-log-runbook.md`, `rollback-plan.md`, `chat-loadtest-and-performance.md`. |

## Observability & Alerts

- [ ] Дашборды из `communications-observability-dashboard.md` развёрнуты и заполнены данными Stage.
- [ ] Алерты отправляют тестовые уведомления (PagerDuty/Slack) и признаются в течение 5 мин.

## Dark launch и включение по feature flags

Последовательность раскатки:

1. **`chat_dark_launch`** — включаем только внутренним пользователям, проверяем дашборды/алерты 24 часа.
2. **`chat_notifications_beta`** — подключаем e-mail/web push для 5% контрактов (feature flag в notification worker). Мониторим drop-rate <1%.
3. **`dispute_tools_v2`** — включаем арбитражные инструменты для команды dispute_ops, убеждаемся, что SLA таймеры работают.
4. **`chat_full_release`** — выкатываем всем пользователям после подтверждения Go. В случае проблем выключаем `chat_full_release` и откатываем на SSE-only режим.

Каждый шаг фиксируется в rollout репорте, а откат производится через LaunchDarkly (max 5 минут).

## Privacy & Legal

- [ ] Документы `data-privacy-policy-communications.md` и условия арбитража опубликованы в Confluence/Help Center.
- [ ] Реализованы механизмы удаления/экспорта данных на Stage (ручная проверка 1 кейса).

## QA

- [ ] Выполнен план `communications-test-plan.md` (unit/integration/e2e/chaos) → все критичные сценарии зелёные.
- [ ] Баги уровня blocker/critical закрыты.

## Решение

- [ ] **Go** — все пункты отмечены.
- [ ] **No-Go** — указать причины, баги, ожидаемый срок повторной проверки.

Подписи: инженер релиза, QA, продукт, юрист.
