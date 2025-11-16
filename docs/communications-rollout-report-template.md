# Communications Rollout Report Template

Используется после деплоя чат/споров/уведомлений на Stage или Prod.

## 1. Release Info

- Дата/время:
- Окно деплоя:
- Версии сервисов (chat-gateway, chat-worker, notification, dispute-service):
- Feature flags включены:

## 2. Go/No-Go Summary

- Stage чек-лист (ссылка/версия):
- Решение: Go / Partial / Rollback
- Основные риски:

## 3. Метрики после деплоя (T+1h / T+24h)

| Метрика | T+1h | T+24h | Цель |
| --- | --- | --- | --- |
| p95 chat latency |
| WS error rate |
| Active connections |
| Disputes overdue |
| Notification delivery success |
| Drop rate |
| NPS after dispute (если доступно) |

## 4. Инциденты / Отказы

- №, время, описание, канал обнаружения, статус, корневая причина, план действий.

## 5. Observability & Alerts

- Проверено, что дашборды обновляются.
- Список алёртов, которые сработали/были потушены.

## 6. Privacy & Compliance

- Подтверждение, что экспорт и удаление работают (если тестировалось).
- Жалобы пользователей (если есть).

## 7. Lessons Learned / Улучшения

- Техдолг, улучшения тестов, наблюдаемости, процессов.

## 8. Follow-up tasks

| Task | Owner | ETA |
| --- | --- | --- |
| |

## 9. Приложения

- Ссылки на графики, логи, PostHog insights, Sentry issues.

Подписанты: инженер релиза, on-call, продукт, юрист.
