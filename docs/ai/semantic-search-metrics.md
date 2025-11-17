# Semantic Search Metrics

## Offline eval
| Корпус | nDCG@5 | nDCG@10 | Recall@20 | Примечание |
| --- | --- | --- | --- | --- |
| Orders (ru+uz) | 0.68 | 0.74 | 0.81 | 9k размеченных запросов (ручной + implicit clicks) |
| Profiles | 0.64 | 0.70 | 0.78 | Учитываем публичные профили, фильтр visibility=public |
| Portfolio | 0.61 | 0.67 | 0.75 | Нормализованный текст problem/solution/result |

Метрики считаем на батчах из ClickHouse лога, baseline — keyword BM25.

## API contract (ai-gateway)
`POST /semantic_search`
```
{
  "query": "mobil ilova", "entity": "orders", "locale": "uz",
  "documents": [
    {"id": "order:1", "title": "Разработка iOS", "body": "Нужно собрать MVP", "tldr": "Кратко: MVP iOS"}
  ],
  "limit": 20
}
```
Ответ: `{ "results": [{"id": "order:1", "score": 0.74, "snippet": "..."}], "fallback_triggered": false, "source": "ai" }`.
Backend проксирует на `/api/marketplace/semantic-search/?query=...&entity=orders`.

## Примеры запросов
| Query | Entity | Топ-результат | Комментарий |
| --- | --- | --- | --- |
| "mobil ilovani ishlab chiqish" | orders | Заказы с тегом `mobile_app`, cosine ≥0.65 | uz→ru нормализация (см. `language-quality-bench-v1.md`). |
| "figma wireframe" | profiles | Дизайнеры с навыками `figma`, `ux` | Используем TL;DR профиля в эмбеддинге. |
| "qadoqlash dizayni" | portfolio | Портфолио с тегами `package_design` | Synonym map `qadoqlash -> packaging`. |

## Реализация требований
- Индексация документов в payload из backend (≤200 объектов, pgvector downstream).
- Семантика + fallback: если `results[0].score < 0.1`, backend использует keyword фильтр (`_fallback_search`).
- SLA: p95 < 300 мс, таймаут 0.9 с на стороне ai-gateway, см. `infra-and-slo-spec.md`.
