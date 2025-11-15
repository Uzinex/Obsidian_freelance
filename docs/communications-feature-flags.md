# Communications Feature Flags

Ниже перечислены фичефлаги, управляющие запуском чатов, споров и уведомлений. Все значения читаются из переменных окружения при старте Django (`backend/obsidian_backend/feature_flags.py`) и попадают в `settings.FEATURE_FLAGS`.

## Перечень флагов и окружений

| Флаг | ENV-переменная | Назначение | Влияние | Dev (по умолчанию) | Stage (по умолчанию) | Prod (по умолчанию) |
| --- | --- | --- | --- | --- | --- | --- |
| `chat.enabled` | `FEATURE_CHAT_ENABLED` | Включает API и WebSocket/SSE каналы чата в контрактах. | Управляет созданием `communications_conversation`, выдачей токенов и `/contracts/{id}/communications`. | `true` — чат доступен всем договорам на деве. | `false` — включаем точечно по мере готовности. | `false` до финального аудита безопасности. |
| `chat.attachments` | `FEATURE_CHAT_ATTACHMENTS` | Разрешает загрузку файлов/медиа в сообщениях. | Выводит UI кнопки вложений и проверку лимитов в backend. | `true` — тестируем сохранение в dev S3. | `false` — на stage разрешаем только текст, пока не закончены анти-бот фильтры. | `false` — до утверждения политики хранения. |
| `chat.presence` | `FEATURE_CHAT_PRESENCE` | Включает публикацию онлайн-статуса участников. | Активирует Redis pub/sub с heartbeat и отображение «в сети». | `true` — для тестирования нагрузки. | `false` — выключено, чтобы не плодить шум в логах. | `false` — включим после оптимизации приватности. |
| `dispute.enabled` | `FEATURE_DISPUTE_ENABLED` | Доступность создания споров и их веток в чате. | Управляет кнопкой «Открыть спор» и API `dispute_thread`. | `false` — пока нет арбитражной команды. | `false` — включается вручную только на пилотных заказах. | `false` до запуска полной службы поддержки. |
| `notify.email` | `FEATURE_NOTIFY_EMAIL` | Рассылка transactional email об обновлениях чата/споров. | Включает постановку задач email-уведомлений и fallback из ADR-0004. | `true` — письма нужны даже в dev для end-to-end тестов. | `true` — отражает боевое поведение. | `true`. |
| `notify.webpush` | `FEATURE_NOTIFY_WEBPUSH` | PWA/web-push уведомления о новых событиях. | Разрешает выдачу push-subscription токенов и постановку задач на webpush-воркер. | `true` — для теста UX. | `false` — запускаем только для QA-группы через ручное включение. | `false` — ждём сертификации Apple. |

## Как включить/отключить чат, споры и нотификации на Stage без redeploy

Stage окружение развёрнуто в Kubernetes и использует deployment `backend-stage`. Менять поведение можно конфигурацией окружения, не пересобирая образ:

1. Обновите нужную ENV-переменную для deployment:
   ```bash
   kubectl set env deployment/backend-stage FEATURE_CHAT_ENABLED=true
   kubectl set env deployment/backend-stage FEATURE_CHAT_ATTACHMENTS=false
   kubectl set env deployment/backend-stage FEATURE_DISPUTE_ENABLED=true
   kubectl set env deployment/backend-stage FEATURE_NOTIFY_EMAIL=true
   kubectl set env deployment/backend-stage FEATURE_NOTIFY_WEBPUSH=false
   ```
   Аналогично отключаем — указываем `=false`.
2. Дождитесь автоматического рестарта podов (kubectl выполнит rolling restart) и убедитесь, что rollout завершился:
   ```bash
   kubectl rollout status deployment/backend-stage
   ```
3. Проверьте, что флаг применился:
   - Вызовите `GET /api/marketplace/contracts/<id>/communications/` — ответ отразит текущее состояние всех флагов.
   - Либо выполните `python manage.py shell -c "from django.conf import settings; print(settings.FEATURE_FLAGS)"` на stage podе.

Процесс не требует новой сборки/деплоя приложения: меняется только значение переменной окружения и автоматически перезапускается deployment.
