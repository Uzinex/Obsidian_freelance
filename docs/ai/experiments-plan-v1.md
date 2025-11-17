# План A/B-экспериментов AI v1

## 1. Инфраструктура
- **Feature flag layer:** LaunchDarkly-подобная прослойка (`ai_coach_v2`, `matching_rerank_v1`, `spam_guard_v2`).
- **Bucketization:** хэшируем `user_id` → 1 000 бакетов, закрепляем на 30 дней, исключаем сотрудников и крупных клиентов.
- **Assignment tables:** см. описание хранилища в итоговом ответе (таблицы `experiments`, `assignments`, `ai_events`).
- **Группы:** минимум 5% контроля, 5–20% теста в зависимости от риска.
- **Длительность:** не менее 7 полных суток и ≥ 2 полных циклов использования (рабочая неделя + выходные).
- **MDE:** считаем по guardrail-метрике (жалобы на AI) — целимся обнаружить изменение 15% при power 0.8.
- **Sequential testing:** применяем SPRT только для ранних остановок при ухудшении >25%.

## 2. Guardrail-метрики
1. **Error rate (HTTP 5xx + AI fallback)** — рост > 2 p.p. ⇒ стоп.
2. **AI complaints / 1k sessions** — рост > 15% ⇒ стоп.
3. **Opt-out AI coach** — рост > 10% ⇒ стоп.
4. **Latency p95** — > +500 мс к контролю ⇒ деградация.
5. **Cost per request** — рост > 20% без компенсирующего бизнес-эффекта ⇒ эскалация.

## 3. План фичей
| Эксперимент | Гипотеза | Метрики эффекта | Размер теста | Допуск в A/B |
| --- | --- | --- | --- | --- |
| `matching_rerank_v1` | Cross-encoder улучшит apply rate | Apply/Job view, MRR онлайн | 20% | nDCG@10 ≥0.50 (выполнено) |
| `ai_coach_personalization` | Персональные советы снизят opt-out | Opt-out, CSAT, human rating | 10% | Win-rate ≥40% |
| `spam_guard_v2` | Новый фильтр снизит жалобы на scam | Scam complaints/1k msgs | 15% | ROC-AUC ≥0.90 |
| `dispute_router_ml` | ML уменьшит время эскалации | Median TTR, accuracy | 10% | Macro-F1 ≥0.65 |

## 4. Процесс запуска
1. Продукт пишет экспериментальный PRD и получает флаг.
2. DS подтверждает, что оффлайн-пороги выполнены.
3. QA проводит dark launch на 1% пользователей.
4. Активация основных бакетов, сбор данных ≥7 дней.
5. Автоматический отчёт (см. `experiment-report-template.md`).

## 5. Каузаьная аналитика
- Используем CUPED для снижения дисперсии по истории взаимодействий.
- Для нерандомизируемых сценариев (например, гео-пилоты) применяем difference-in-differences с контрольной группой из соседних регионов.
- Все события пишутся в `ai_ab_metrics` с timestamp, variant и user covariates.

## 6. Структура хранилища событий
| Таблица | Ключевые поля | Назначение |
| --- | --- | --- |
| `experiments` | `experiment_id`, `flag`, `owner`, `start_ts`, `end_ts`, `status` | Каталог активных/архивных экспериментов. |
| `experiment_variants` | `experiment_id`, `variant_id`, `name`, `traffic_share` | Настройки вариантов (control/test). |
| `experiment_assignments` | `user_id`, `experiment_id`, `variant_id`, `bucket_id`, `assigned_ts`, `exposure_ts` | Фиксирует бакет и первую экспозицию пользователя. |
| `ai_events` | `event_id`, `user_id`, `experiment_id`, `variant_id`, `event_type`, `payload`, `cost_micro`, `latency_ms`, `language`, `embedding_stats` | Все AI-взаимодействия (коуч, matching, фильтры) для аналитики и дрейфа. |
| `ai_request_costs` | `request_id`, `model`, `tokens_in/out`, `cost_micro`, `cache_hit`, `qps_bucket` | Для FinOps-отчётов и guardrail-метрик по стоимости. |
| `ai_feedback` | `event_id`, `user_id`, `label` (useful/not useful), `comment`, `manual_edit_flag` | Источник онлайн-метрик качества. |

Все таблицы живут в ClickHouse (raw) + дублируются в BigQuery для дашбордов. Партиционирование по `event_date`. В `ai_events.payload` сохраняем ключевые признаки (job_id, profile_id, dispute_id), чтобы связывать с оффлайн-датасетами.

