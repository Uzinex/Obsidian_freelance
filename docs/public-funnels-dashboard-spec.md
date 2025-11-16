# Наблюдаемость и воронки (public)

## События (frontend `trackEvent`)
| Event | Где триггерится | Payload |
| --- | --- | --- |
| `landing_view` | `HomePage` `useEffect` | `{ locale }` |
| `landing_signup_click` | CTA «Начать сейчас» | `{ locale, authenticated }` |
| `landing_post_job_click` | CTA «Смотреть работы» | `{ locale, authenticated }` |
| `landing_invite_freelancer` | CTA «Пригласить фрилансера» | `{ locale }` |
| `section_viewport_enter` | `useScrollTelemetry` (hero, categories, steps, orders) | `{ section, locale }` |
| `escrow_benefit_click` | Карточки преимуществ escrow | `{ locale, feature }` |
| Ошибки данных | `trackError('landing_data_error', error)` | `{ locale, stack }` |

## Дашборды
1. **Conversion by locale** (Looker Studio / Grafana)
   - Метрики: `landing_view` → `landing_signup_click`, `landing_post_job_click` по `locale`.
   - Виджеты: stacked bar (ru/uz), таблица CR.
2. **UTM behavior**
   - События дополняем `utm_source` (будет парситься в `trackEvent`).
   - Heatmap: какие UTM приводят к `landing_post_job_click`.
3. **Escrow engagement / click map**
   - Карточки escrow + scroll events → воронка (`section_viewport_enter:escrow` → `escrow_benefit_click`).
   - Тултип-карта (через Yandex Metrica или Hotjar) для подтверждения кликов.

## Alerts
| Метрика | Условие | Канал |
| --- | --- | --- |
| Conversion drop | Если CR (signup или post job) < 1.5% в течение 2 часов (по каждой локали) | Slack `#growth-alerts` |
| 404 spike | Cloudflare/Edge логика: > 50 404 за 5 минут на `/ru/*` или `/uz/*` | PagerDuty (L2) |
| SSG build errors | `npm run build:ssg` → при `stderr`/exit != 0 отправляем webhooks в Sentry Release Monitor | Slack `#infra` |

## Инфраструктура
- Источник событий: `window.dataLayer` (см. `frontend/src/utils/analytics.js`).
- Сбор: GTM → GA4 + BigQuery (`public_pages` dataset).
- Дедупликация: используем `timestamp` + `event` как первичный ключ.
- Хранение регламентов: `/docs/public-funnels-dashboard-spec.md` (этот файл) + Confluence page `Growth/Public funnels`.
