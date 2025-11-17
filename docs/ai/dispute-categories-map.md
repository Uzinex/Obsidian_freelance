# Dispute Categories Map

Категории помогают быстро классифицировать спор и показать модератору релевантные правила. Каждая категория содержит критерии, ключевые факты для проверки и ссылки на Terms.

| Код | Название | Критерии | Что проверить | Terms/Policies |
| --- | --- | --- | --- | --- |
| `non_delivery` | Неисполнение / ничего не сдано | Нет файлов или прогресса после дедлайна. | Сверить обещанные и загруженные файлы, проверить логи активности. | `dispute-policy.md`, `dispute-outcome-escrow-map.md`. |
| `late_delivery` | Просрочка | Работа сдана, но позже согласованной даты. | Таймлайн милстоунов, подтверждения переносов. | `sla-timers-and-actions.md`. |
| `quality_issue` | Низкое качество / несоответствие ТЗ | Файлы есть, но не проходят чек-листы качества. | Acceptance criteria, ревью, комментарии заказчика. | `prod-ready-checklist.md`, `tone-and-style-guide-v1.md`. |
| `scope_creep` | Спор по объёму работ | Клиент просит больше, чем в договорённости. | Переписка на момент согласования, наличие доп. оплат. | `dispute-policy.md`, `rate-limit-policy.md`. |
| `payment_issue` | Не подтверждён платёж / возврат | Спор по выплатам или возврату эскроу. | Статусы платежей, escrow события. | `chat-escrow-events-map.md`, `dispute-decision-template.md`. |
| `conduct_violation` | Нарушение поведения | Оскорбления, шантаж, попытки вывести оплату. | Скриншоты чатов, жалобы. | `chat-moderation-policy.md`, `security-testing.md`. |

## Логирование сигналов
- `dispute.category_suggested` — `{dispute_id, category, confidence}`.
- `dispute.category_overridden` — `{dispute_id, previous_category, new_category, moderator_id}`.
- `dispute.rules_referenced` — `{dispute_id, policy_docs}`.
Эти события помогают отслеживать, насколько подсказки совпадают с финальными решениями модераторов.
