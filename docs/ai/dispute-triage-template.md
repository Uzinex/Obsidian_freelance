# Dispute Triage Case Summary Template

> ⚠️ **Подсказка для модератора. Никаких автоматических решений/выплат.**

## 1. Метаданные
- `dispute_id`:
- `order_id`:
- `opened_at`:
- `initiator` (client|freelancer|system):

## 2. Что было обещано
- Короткое описание задачи
- Ключевые требования / acceptance criteria (список)
- Согласованные сроки / milestone цели

## 3. Что было сдано
- Итоговые файлы или ссылки
- Описание фактически выполненных работ
- Отметка о прохождении ревью/приёмки

## 4. Сроки и милстоуны
| Milestone | Due date | Delivered | Delta | Комментарий |
| --- | --- | --- | --- | --- |

## 5. Платежи
| Payment | Amount | Status | Дата | Комментарий |
| --- | --- | --- | --- | --- |

## 6. Предположимая категория спора
- `category_hint` (из карты категорий)
- Обоснование (факты + ссылки на переписку)
- `confidence` (high/medium/low). Если low → тег «нужна ручная проверка».

## 7. Релевантные сообщения/файлы
- Список `{message_id, sender_role, timestamp, summary, url}`
- Список `{file_id, type, checksum, url}`

## 8. Чек-лист модератора
- Какие правила/Terms пересмотреть (например, `dispute-policy.md`, `escrow-terms`)
- Что проверить в первую очередь (подтвердить сроки, сверить принятые файлы, уточнить доп. работы)
- Поля для заметок модератора

## 9. Сигналы для логов/аналитики
- `dispute.summary_generated` — `{dispute_id, category_hint, confidence}`
- `dispute.manual_checklist_completed` — `{dispute_id, completed_items}`
- `dispute.escalation` — `{dispute_id, reason}`

**Памятка:** Никаких автоматических выплат, штрафов или блокировок — решение принимает модератор после просмотра всех материалов.
