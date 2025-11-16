# Публичные страницы: производительность и кэш

## Цели Web Vitals
| Метрика | Цель | Как достигаем |
| --- | --- | --- |
| LCP | < 2.5s на 4G, < 4.0s на 3G | SSG/ISR для всех лендингов (`frontend/ssg.config.mjs`), критический блок hero в `src/styles.css`, предзагрузка шрифтов. |
| CLS | < 0.1 | Фиксированные размеры для карточек и иллюстраций, `font-display: swap` в `styles.css`, sticky-хедер без динамических вставок. |
| INP | < 200ms | Минимум эффектов при скролле, обработчики кликов (CTA, escrow) только при взаимодействии. |

## CSS и загрузка медиа
- Глобальный шрифт `Inter` подключён c `display=swap` + подмножества `latin-ext`/`cyrillic` (`frontend/src/styles.css`).
- Применяем lazy-loading/`decoding="async"` для декоративных картинок на лендинге и About.
- Герой и основные карточки описаны в общем CSS-файле; для критических стилей допускается инлайн через Vite `styleTag` (todo в `docs` backlog).

## Preconnect/Prefetch
- `frontend/index.html` содержит preconnect к `fonts.googleapis.com`, `fonts.gstatic.com`, `cdn.obsidianfreelance.com`.
- Для будущих edge-функций CDN (Fastly/Cloudflare) добавим `preload` для критичных скриптов (описано в backlog).

## Кэширование и CDN
- Вся статика (`dist/`) отдаётся через CDN с ключом `locale + path` (например `ru:/faq`).
- Политика `Cache-Control: public, max-age=86400, stale-while-revalidate=604800` для лендингов; для блога `max-age=21600`.
- API-запросы категорий/заказов – через origin c `stale-if-error=120` (добавим в backend gateway).
- SSG генератор (`frontend/scripts/prerender.mjs`) пересобирает страницы согласно `revalidate` интервалам; на CDN настраиваем webhook чтобы сбрасывать конкретный путь.

## План тестирования
- Lighthouse (mobile) прогоняется на `npm run build && npm run preview` – фиксируем LCP/CLS.
- WebPageTest (3G/Slow 4G) – сценарии: загрузка `/ru`, `/ru/escrow`, `/ru/blog/escrow-playbook`.
- CrUX Monitoring: проект `obsidian-public` в Google Cloud собирает реальные метрики; пороги — алёрт если LCP P75 > 3s три дня подряд.
