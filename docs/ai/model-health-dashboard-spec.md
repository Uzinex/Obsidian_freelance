# Model Health Dashboard Spec

## 1. Цели
- Мониторить онлайн-качество AI-компонентов (matching, coach, фильтры).
- Детектировать дрейф данных и рост «неполезных» подсказок.

## 2. Структура дашборда
1. **Overview таб**
   - Health score per модель (0–100, агрегат по метрикам ниже).
   - Последние алёрты и статус (Active/Acknowledged/Resolved).
2. **Embedding Drift таб**
   - TSNE/UMAP snapshot по неделям.
   - KL-divergence и PSI между текущей неделей и эталоном.
   - Distribution per language (ru, uz, mixed).
3. **Coach Quality таб**
   - Частота «неполезных» подсказок (user feedback кнопка) — цель <8%.
   - Частота ручных правок коуча (редактирование модератором) — цель <5%.
   - Win-rate human review (rolling 7d).
4. **Matching таб**
   - Online nDCG@10 proxy (implicit apply signals).
   - CTR на рекомендации и conversion в отклик.
5. **Filters таб**
   - ROC proxy: TPR/FPR на жалобах.
   - Жалобы на scam/spam per 1k сообщений.

## 3. Метрики и алёрты
| Метрика | Источник | Порог | Алёрт |
| --- | --- | --- | --- |
| Embedding PSI (skill dimension) | `ai_embedding_metrics` | >0.25 | Drift alert «Embedding shift» |
| Coach non-useful rate | feedback events | >8% 2 дня подряд | «Coach useless spike» |
| Manual edits per 1k sessions | moderator tool | >50 | «Coach handoff overload» |
| Matching online nDCG proxy | apply logs | <0.45 | «Matching quality drop» |
| Scam complaints | support logs | +20% WoW | «Scam surge» |

## 4. Реобучение / Перетест
- **Планово:** раз в месяц обновлять эмбеддинги и классификаторы, после чего запускать оффлайн-оценку и sanity-check онлайн.
- **По событию:** если любой алёрт активен >24 часов, запускаем fast-track:
  1. Сбор свежего датасета (минимум 200 примеров).
  2. Переобучение модели.
  3. Повторный оффлайн-репорт (сокращённый) + dark launch на 1%.

## 5. Интеграции
- Источник данных — ClickHouse `ai_events` + `ai_request_costs` + feedback API.
- Алёрты через Grafana → Slack `#ai-ops` + PagerDuty для критичных (embedding drift, scam surge).
- Хранение baseline распределений — S3 `s3://ai-metrics/baseline/v1/`.

