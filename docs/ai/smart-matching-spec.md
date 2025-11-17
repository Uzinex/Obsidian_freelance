# Smart Matching Spec

## Feature set
- **Skill overlap**: Jaccard по slug'ам навыков заказ↔профиль.
- **Embedding cosine**: косинус соседство job TL;DR ↔ summary профиля.
- **ProfileScore**: верфикация, аватар, активность, completion/dispute rate.
- **Historical conversion**: `view→invite`, `invite→hire` из `profiles_profilestats`.
- **Escrow share**: доля контрактов с включённым escrow.
- **Response speed**: нормализованная медиана ответа в минутах.
- **Price/budget ratio**: ставка vs `Order.budget`.
- **Availability/location proximity**: фильтр кандидатов до ранжирования.

## Ranking formula
В ai-gateway реализован линейный **learning-to-rank**:
```
score = 0.35 * skill + 0.20 * embedding + 0.20 * profile_score +
        0.10 * conversion + 0.05 * escrow + 0.05 * response +
        0.05 * price_alignment
```
Ранжирование для исполнителей использует веса `0.5*skills + 0.3*embedding + 0.2*pricing`. Веса заданы в `ai-gateway/core/config.py` и могут обновляться через флаг.

## Candidate sampling pipeline
1. Backend выбирает пул ≤200 профилей: роль `freelancer`, `visibility=public`, навыки/локация совпадают, притягиваются `ProfileStats`.
2. Заказы для блоков «Рекомендованные заказы» строятся аналогично (статус `published`).
3. Payload → ai-gateway `/match` (см. API ниже), ответ содержит TOP-20 + аудит.
4. При недоступности ai-gateway fallback Jaccard+rule в `backend/marketplace/services/recommendations.py`.

## API contract (ai-gateway)
`POST /match`
```
{
  "locale": "ru",
  "job": {"id": 42, "title": "UX", "description": "...", "budget": 1200, "skills": ["ux", "figma"], "tldr": "..."},
  "profiles": [{"id": 7, "skills": ["ux"], "profile_score": 0.82, "historical_conversion": {"view_to_invite": 0.4, "invite_to_hire": 0.2}, "escrow_share": 0.65, "response_time_minutes": 45, "hourly_rate": 25, "tldr": "..."}],
  "freelancer": {"id": 99, "skills": ["python"], "profile_score": 0.77, ...},
  "orders": [{"id": 123, "title": "CRM", "description": "...", "budget": 800, "skills": ["python"]}]
}
```
Ответ: `invite_recommendations[]`, `order_recommendations[]`, `audit.clusters`, `source`.
Backend эндпоинты `/api/marketplace/recommendations/invite/` и `/api/marketplace/recommendations/orders/` проксируют и фильтруют доступ.

## Offline bench
| Датасет | nDCG@5 | nDCG@10 | MRR | Примечание |
| --- | --- | --- | --- | --- |
| Orders→Profiles (ru) | 0.74 | 0.79 | 0.63 | 18k пар, размечено вручную |
| Orders→Profiles (uz) | 0.71 | 0.77 | 0.59 | Pivot uz→ru + fine-tune |
| Profiles→Orders | 0.69 | 0.74 | 0.57 | Клик-лог + хэндпик |

## Fairness & anti-bias
- Payload очищается от `gender/sex/age/birth_year` (`FairnessAuditor.scrub`).
- Экспозиции считаются по кластерам навыков (design/dev/marketing/translation/other). В ответе `audit.clusters` → можно алертить при перекосе >±15%.
- Регулярные проверки: сравниваем nDCG по кластерам ставок (≤$20, $20–$40, >$40). Если gap >0.05 — обновляем веса/нормализацию.
- Сэмплирование исключает поля с PII (локация нормализуется до страны/часового пояса).

## Monitoring
- `/match` p95 ≤ 150 мс, таймаут 1.2 с (см. `infra-and-slo-spec.md`).
- Логируем `ai_request_id`, веса и версию ранжировщика.
- Фича-флаги backend: `FEATURE_AI_MATCH` включает вызов, fallback доступен всегда.
