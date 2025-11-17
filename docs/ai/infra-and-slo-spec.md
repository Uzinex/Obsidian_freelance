# Infra & SLO Spec

## Стек инференса
- **Векторный слой**: PostgreSQL 15 + `pgvector` (768-d float) для индекса HNSW, поддержка upsert и TTL.
- **Модели**: открытые веса (например, `intfloat/multilingual-e5-large` для эмбеддингов и `Nous-Hermes-2-Mistral-7B` fine-tuned на ru/uz). Деплой через GPU-пулы (A10/A100) в k8s, autoscaling по очереди задач.
- **Внешние API**: допускаются за фичефлагом (пример — `openai/gpt-4o-mini`) с бюджетными квотами и мониторингом стоимости.
- **Кэш**: Redis Cluster для результатов эмбеддингов и подсказок.

## Сервис ai-gateway
Отдельный backend (FastAPI) с модулями:
```
ai-gateway/
  app.py
  core/
    auth.py
    rate_limits.py
    tracing.py
    cache.py
  clients/
    embeddings.py
    rerank.py
    generator.py
  routers/
    embeddings.py      -> POST /embeddings
    match.py           -> POST /match
    coach.py           -> POST /coach
    spam_filter.py     -> POST /spam_filter
    dispute_summary.py -> POST /dispute_summary
    semantic_search.py -> POST /semantic_search
    summaries.py       -> POST /summaries
  workers/
    offline_summaries.py
    cache_warmup.py
```

### Политики
- **Таймауты**: 1.5s для embeddings/match/search, 2.0s для coach/dispute/summaries (со streaming).
- **Квоты**: per-user 60 запросов/минуту на match/search, 20/мин на coach, 10/мин на dispute. Per-org лимиты выше в 5x.
- **Трейсинг и логирование**: OpenTelemetry + OTLP sink; поля без PII, корелляция по `ai_request_id`.
- **Кэширование**:
  - Эмбеддинги: ключ `embedding:{model}:{hash(text)}` TTL 24h.
  - Подсказки: ключ `prompt:{locale}:{hash(payload)}` TTL 2h.

## SLO
| Поток | Цель | SLO |
| --- | --- | --- |
| Эмбеддинги / ранжирование | Fast-path | p95 ≤ 150–200 мс |
| Генерация подсказки (coach, dispute) | Streaming | p95 ≤ 1.5–2.0 с |
| AI-резюме карточек | Offline | выполняется асинхронно, при запросе только чтение ≤ 50 мс |

## Квоты и среда
- Глобальные квоты фиксируются в консоли feature flags и в конфиге ai-gateway; превышение → HTTP 429 + совет.
- Разделяем лимиты по окружениям: Dev (умножение ×0.1), Stage (×0.5), Prod (×1.0).
- Для внешних API отслеживаем дневной бюджет, при превышении — автоматический disable флага `ai.external_provider`.
