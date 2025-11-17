# TL;DR Guidelines

## Length & tone
- 160–200 символов, не более 2 предложений.
- Язык совпадает с локалью (`ru` или `uz`), тон деловой (см. `language-quality-bench-v1.md`).
- Начинаем с явного маркера (`Кратко:` / `Qisqa sharh:`), затем суть + CTA/статус.
- Без маркетинговых штампов, без точных обещаний сроков.

## Structure
1. **Context**: что за заказ/профиль (роль, ключевой навык).
2. **Ценность**: бюджет/результат/опыт.
3. **Статус**: срочность, формат, требования.

## Storage & usage
- Поля `Order.tldr_ru/tldr_uz`, `Profile.tldr_ru/tldr_uz`, кеш `ai:tldr:{entity}:{id}:{locale}` (`backend/obsidian_backend/ai/tldr.py`).
- Offline генерация `python manage.py generate_tldr --entity=orders --locale=ru` → сохранение + warm cache.
- Карточки: сериализаторы `OrderSerializer` и `ProfileSerializer` подхватывают TL;DR по `Accept-Language` → отображение в списках/поиске/лендингах.

## Examples
| Case | Good TL;DR | Bad TL;DR |
| --- | --- | --- |
| Order: разработка CRM | `Кратко: Нужен backend-разработчик для CRM на Django, бюджет $4k, старт в октябре, обязательны интеграции с платежами.` | `Лучший проект! Срочно нужно всё сделать за день, платим много.` |
| Profile: UX дизайнер | `Qisqa sharh: 5 yillik Figma/UX tajribasi, mobil ilovalar uchun oqimlar va A/B testlar, tayyor remote.` | `Я делаю любой дизайн, просто напишите.` |

## Quality checks
- language-quality-bench sanity (`mobil ilovani ishlab chiqish` → `разработка мобильного приложения`).
- A/B: CTR карточек с TL;DR vs baseline ≥ +10%. Metrics храним в `public-funnels-dashboard-spec.md`.
