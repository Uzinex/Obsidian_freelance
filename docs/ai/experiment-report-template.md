# Experiment Report Template

## 1. Metadata
- **Experiment name / flag:**
- **Owner:**
- **Hypothesis:**
- **Start / End dates:**
- **Traffic split (control/test):**
- **Guardrails monitored:**

## 2. Data Quality Checklist
- [ ] Бакеты стабильны (no churn >1%).
- [ ] Нет rollout-исключений (blocked geo, segments).
- [ ] Логи событий в `ai_events` без пропусков (<0.5%).

## 3. Primary metrics
| Metric | Control | Test | Δ | p-value | Interpretation |
| --- | --- | --- | --- | --- | --- |

## 4. Guardrail metrics
| Metric | Control | Test | Δ | Threshold | Status |
| --- | --- | --- | --- | --- | --- |

## 5. Diagnostics
- **Latency:** p50 / p95 / tail.
- **Cost:** ₽ / ₮ per 1k requests, cache hit rate.
- **User feedback:** жалобы, opt-out, qualitative quotes.

## 6. Causal adjustments
- Применён ли CUPED / DiD? Формула и результаты.
- Covariates использованы.

## 7. Decision
- ✅ Rollout / ⚠️ Iterate / ❌ Abort.
- Обязательные действия (миграция флага, коммуникация).

## 8. Learnings & Follow-ups
- Что улучшить перед следующим экспериментом.
- Новые гипотезы.

