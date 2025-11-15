# Матрица исходов спора и escrow-операций

| Исход | Описание | Escrow действие | Доп. параметры |
|-------|----------|-----------------|----------------|
| `full_release` | Полный релиз средств исполнителю | `escrow.release_full(contract_id)` | Нет |
| `partial_release` | Делёжка средств по долям | `escrow.release_partial(contract_id, client_share)` | `payload.client_share` — доля клиента (0..1). Остальное получает исполнитель |
| `refund` | Полный возврат клиенту | `escrow.refund(contract_id)` | Требуется подтверждение finance |

## Ограничения
- Доступные операции выбираются из выпадающего списка, ручной ввод суммы недоступен.
- В payload могут храниться метаданные (`reason_code`, `client_share`). Значения валидируются сервисом `disputes.services.record_outcome`.
- Все транзакции логируются в `moderation_staffactionlog` и в журнале кошельков.
