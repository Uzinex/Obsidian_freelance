# A11y + мобильная адаптация (public)

## Контраст и цвет
- Минимум 4.5:1 для текстов `< 18pt`. Проверяем через `axe DevTools` и ручные измерения (hero, CTA, карточки).
- Цвета из `styles.css` проходят WCAG AA; при изменениях обновляем палитру в документации.

## Фокус и клавиатура
- Все интерактивные элементы имеют видимый `:focus` (кнопки, ссылки, карточки escrow с `role="button"`).
- Проверяем табуляцию (Shift+Tab/Tab) для `/ru`, `/ru/escrow`, `/ru/blog/*`.

## Семантика и aria
- Хедеры используют последовательную иерархию (`h1` → `h2`).
- Кнопки CTA используют `<button>` или `<Link>` с корректным текстом (нет «клик сюда»).
- Карточки с ролью «button» получают `tabIndex` и обработку `Enter` (см. Escrow).

## Читабельность uz/ru
- `publicContent` содержит локализованные описания, без транслита.
- Шрифт Inter поддерживает кириллицу/латиницу, `font-display: swap` исключает FOIT.

## Мобильные проверки
1. **Android (Pixel 6, 360×800, DPR 3)** – Chrome devtools, профиль: `/ru` и `/ru/escrow`.
2. **iOS (iPhone 14, 390×844)** – Safari responsive mode.
3. **3G тест** – Chrome devtools «Fast 3G» для `/ru/blog/escrow-playbook`.

## A11y lint/tests
- `npm run dev` + `npx @axe-core/cli http://localhost:5173/ru` – быстрый аудит.
- `npx playwright install` + `npx @axe-core/playwright --browser chromium --save ./reports/a11y.json http://localhost:5173/ru/faq`.
- Добавлено обязательное ревью чек-листа перед релизом.
