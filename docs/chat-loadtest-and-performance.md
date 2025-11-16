# Chat Load Test & Performance Plan

Документ описывает целевые показатели производительности коммуникационного сервиса, методику нагрузочного тестирования и политику отказоустойчивости (fallback).

## Цели производительности

| Метрика | Цель | Примечания |
| --- | --- | --- |
| p95 latency отправки сообщения (API → доставка WS/SSE) | ≤ 1 сек | p99 ≤ 2 сек. |
| Throughput сообщений | ≥ 2 000 msg/сек (кластер) | 500 msg/сек на инстанс. |
| Одновременные пользователи | ≥ 20 000 активных соединений | Проверяем WS и SSE. |
| Ошибки доставки | ≤ 0.5% | Включая ретраи. |
| Фэйловер на polling/SSE | ≤ 3 сек на переключение | Client SDK обязан перейти автоматически. |

## Нагрузочный тест

### Инфраструктура

- **Инструмент**: k6 + ws библиотека, сценарии в `infrastructure/loadtests/chat/`.
- **Топология**: отдельный namespace в Stage с autoscaling=off (фиксированные 3 pods gateway + 2 pods workers + Redis, Postgres реплика).
- **Данные**: фикстуры 5k контрактов, 10k пользователей (скрипт `seed_chat_stage.py`).

### Сценарий k6 (псевдокод)

```javascript
import ws from 'k6/ws';
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '2m', target: 2000 },
    { duration: '5m', target: 2000 },
    { duration: '2m', target: 0 },
  ],
  thresholds: {
    'ws_duration{type:send}': ['p(95)<1000', 'p(99)<2000'],
    'http_req_failed': ['rate<0.005'],
  },
};

export default function () {
  const token = http.post(`${BASE_URL}/auth/token`, creds).json('token');
  const thread = pickThread();
  ws.connect(`${WS_URL}?token=${token}`, (socket) => {
    socket.send(JSON.stringify({ type: 'join', thread }));
    socket.on('message', () => {});
    socket.setInterval(() => {
      const payload = buildMessage(thread);
      const start = Date.now();
      socket.send(JSON.stringify(payload));
      socket.on('message', (msg) => {
        if (msg.ack === payload.id) recordDuration('ws_duration', Date.now() - start);
      });
    }, 1000 / MESSAGES_PER_SEC);
    socket.setTimeout(() => socket.close(), 60000);
  });
  sleep(1);
}
```

### Показатели

- Фиксируем `messages_sec`, `active_connections`, `delivery_latency_ms`, `ws_error_rate`.
- Репорт формируется `k6 run chat_load.js --out json=chat_load.json` → `python summarize_load.py chat_load.json` (генерирует Markdown).

### Автоматизация

1. GitHub Action `loadtest-chat.yml` запускается по тегу `stage-loadtest-*`.
2. Action поднимает Stage namespace, разворачивает версии образов, прогоняет `k6` в self-hosted runner.
3. Результаты + графики загружаются в S3 и встраиваются ссылкой в `docs/chat-loadtest-and-performance.md` (секция «Последний прогон»).
4. Action валится, если любые пороги нарушены → блокирует merge через required status.

## Fallback при падении WebSocket

### Автоматический переход

- Client SDK отслеживает `ping_timeout` > 10 сек либо закрытие кода `1006/1011`.
- При 2 последовательных сбоях используется последовательность fallback: **WS → SSE → HTTP polling**.
- SSE эндпоинт `GET /chat/events?thread_id=...` поддерживает авторизацию теми же токенами.
- Polling запросы выполняются каждые 5 сек с ETag, чтобы минимизировать трафик.

### Backoff и защита от штормов переподключений

- Экспоненциальный backoff: `delay = min(2^attempt * 500ms, 30s)` + джиттер ±20%.
- После 5 неудачных попыток клиент переключается на SSE на 2 минуты, далее повторяет WS.
- Gateway ведёт метрику `ws_reconnect_attempts` и при превышении 10/минуту на IP отвечает HTTP 429.
- Для мобайла предусмотрен random spread (0-3 сек) перед первым реконнектом.

## Мониторинг во время теста

- Prometheus dashboard «Chat Loadtest»: `chat_ws_delivery_latency_ms`, `chat_ws_active_connections`, `chat_ingress_cpu`.
- Sentry release alert «chat-stage-load» на ошибки WS gateway.
- Логи gateway анализируются `kubetail chat-gateway -n stage-chat`.

## Последний протокол

> После первого прогона заполнить таблицу:
>
> | Дата | Билд | Активных соединений | msg/сек | p95 латентность | Ошибки | Итог |
> | --- | --- | --- | --- | --- | --- | --- |
> | TBD | TBD | TBD | TBD | TBD | TBD | TBD |

