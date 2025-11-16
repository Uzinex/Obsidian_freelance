# Formatting spec v1

## Общие принципы
- Базовая локаль платформы — `ru` с бэкапом `uz`. Любая неизвестная локаль нормализуется до `ru` → `uz` → системный дефолт.
- Базовая временная зона для отображения и расчётов — `Asia/Tashkent`. Все серверные таймстампы приводим к UTC, в UI и письмах конвертируем к ташкентскому времени.
- Основная валюта — `UZS`. Значения в других валютах допускаются, но по умолчанию отображаем суммы в сумах.
- Библиотеки:
  - браузер/Node: `Intl.NumberFormat`, `Intl.PluralRules`, `dayjs` + плагины `utc`, `timezone`, `localizedFormat`;
  - backend: стандартные `datetime`, `zoneinfo`, `decimal`, кастомные хелперы в `backend/notifications/formatting.py` без дополнительных зависимостей;
  - правило плюрализации — `Intl.PluralRules` (frontend) и зеркальная реализация в backend.

## Числа и суммы
| Локаль | Формат чисел | Десятичный разделитель | Пробел тысяч | Пример |
|--------|--------------|------------------------|---------------|--------|
| ru     | `1 234 567,89` | `,` | неразрывный пробел | `1 200 000` |
| uz     | `1 234 567.89` | `.` | неразрывный пробел | `1 200 000.5` |

- Для `UZS` всегда показываем без копеек/тийинов (`minimumFractionDigits = 0`).
- Подпись валюты:
  - ru: `сум` (пример: `1 500 000 сум`),
  - uz: `so'm` (пример: `1 500 000 so'm`).
- Для остальных валют сохраняем ISO код после суммы (например, `1 200 USD`).
- Хелперы: `formatCurrency`, `formatNumber` в `frontend/src/utils/formatting.js` и `backend/notifications/formatting.py`.

## Даты и время
- Базовый формат даты: `DD.MM.YYYY` (обе локали).
- Базовый формат даты+времени: `DD.MM.YYYY HH:mm` (24 часа, leading zero).
- Для человеко-понятных дат используем relative-хелпер с ключевыми словами:
  - ru: `сегодня`, `вчера`, `завтра`, `через X {дней}` / `X {дней} назад`;
  - uz: `bugun`, `kecha`, `ertaga`, `yana X kun ichida`, `X kun oldin`.
- Граничные кейсы: переключение на относительный формат, если событие ≤7 дней от текущей даты.
- Хелперы: `formatDate`, `formatDateTime`, `formatRelativeDate` на frontend и backend.

## Плюрализация
- Используем категории `one`, `few`, `many`, `other`.
- Примеры:
  - ru (заказы): `{count} {pluralize('ru', count, {one: 'заказ', few: 'заказа', many: 'заказов'})}`;
  - uz (время): `{count} {pluralize('uz', count, {one: 'soat', other: 'soatlar'})}`.
- На frontend — `formatPlural(count, locale, forms)` из `formatting.js`. На backend — `format_plural` из `backend/notifications/formatting.py`.

## Реализация хелперов
- **Frontend:** `frontend/src/utils/formatting.js`
  - нормализация локали + кэшированные `Intl.NumberFormat`/`Intl.PluralRules`.
  - экспортируем `formatCurrency`, `formatNumber`, `formatDate`, `formatDateTime`, `formatRelativeDate`, `formatPlural`, `resolveLocale`.
- **Backend:** `backend/notifications/formatting.py`
  - зеркальные функции форматирования для e-mail и push.
  - сохраняем выбор `Asia/Tashkent`, единый список fallback-локалей.

## Использование
- UI/React: заменить все вызовы `toLocaleString`, ручные конкатенации сумм и дат на хелперы из `formatting.js`.
- Письма/пуши: шаблоны в `backend/notifications/copy.py` используют отформатированные поля `amount_formatted`, `deadline_formatted`, `relative_due`, которые подставляются через хелперы при рендере.
- Фолбэк локали: `locale` из профиля/настроек → `ru` → `uz`. Если даже `uz` недоступен, используем `ru` как стабильный дефолт и логируем предупреждение (см. `emails.py`).

## Относительные фразы
- Интервалы ≤24 часов: отображаем `сегодня/bugun`, `вчера/kecha`, `завтра/ertaga`.
- Интервалы в диапазоне 2–7 дней: `через X {дней}` / `yana X kun ichida` или `X {дней} назад` / `X kun oldin`.
- >7 дней: используем полный формат даты.

## Ссылки на библиотеки и конфигурацию
- JS: `dayjs` и плагины описаны в `package.json`, `Intl` используется напрямую.
- Python: стандартные модули + `zoneinfo.ZoneInfo('Asia/Tashkent')`.
- Все настройки собраны в одном месте и документированы в этом файле для включения QA в чек-листы.
