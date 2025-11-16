# Публичные SEO-мета-данные

## Метатеги и ссылки
| Блок | Детали | Источник |
| --- | --- | --- |
| `<title>` и `<meta name="description">` | Локализованные тексты для каждой страницы (см. `publicContent`), подключаются через `SeoHelmet`. | `frontend/src/components/SeoHelmet.jsx`, `frontend/src/mocks/publicContent.js` |
| Canonical | `https://obsidianfreelance.com/{locale}{path}` – строится через `buildAbsoluteUrl`. | `frontend/src/context/LocaleContext.jsx` |
| hreflang | Пары `ru`, `uz` + `x-default`, формируются на основании текущего маршрута. | `frontend/src/components/SeoHelmet.jsx` |
| robots | Индивидуальные страницы (`Terms/Privacy/Cookies`) получают `noindex`. | `frontend/src/pages/public/TermsPage.jsx`, `.../PrivacyPage.jsx`, `.../CookiesPage.jsx` |
| OG/Twitter | Для каждой страницы прокидываются локализованные `title/description/ogImage`, Twitter-аккаунт зависит от локали. | `frontend/src/components/SeoHelmet.jsx`, `frontend/src/mocks/publicContent.js` |

## JSON-LD схемы
| Страница | Тип | Поля |
| --- | --- | --- |
| Лендинг, About, Contacts | `Organization` | `name`, `url`, `logo`, `sameAs`, `aggregateRating`. |
| Escrow | `Service` + `AggregateRating` + массив `Review`. |
| FAQ | `FAQPage` + `Question/Answer` для каждой записи. |
| Блог | `Blog` и `Article` с `headline`, `datePublished`, `author`, `image`, `articleSection`. |
| Публичные профили | `Person` (`jobTitle`, `knowsAbout`, `description`). |

## OG/Twitter карточки
- **Главная (ru):**
  - `og:title`: `Obsidian Freelance — IT-платформа с безопасным escrow`
  - `og:description`: `Соединяем компании и фрилансеров ...`
  - `og:image`: `https://cdn.obsidianfreelance.com/meta/ru-home.png`
  - `twitter:site`: `@obsidian_ru`
- **Главная (uz):** аналогично с `og:image=https://cdn.obsidianfreelance.com/meta/uz-home.png`, `twitter:site=@obsidian_uz`.
- **Профиль специалиста:**
  - `og:title`: `{Имя} — Публичный профиль специалиста Obsidian Freelance`
  - `og:image`: `https://cdn.obsidianfreelance.com/meta/profile.png`
- **Блог/статьи:**
  - `og:type`: `article`
  - `article:published_time`: через JSON-LD, картинка из `article.cover`.

## Sitemap и robots
- `frontend/public/robots.txt` – открывает публичные страницы, закрывает `/api`, `/staff`.
- `frontend/public/sitemap.xml` – индекс для RU/UZ карт.
- `frontend/public/sitemap-ru.xml`, `sitemap-uz.xml` – актуальные пути (лендинг, escrow, FAQ, блог, профили, юридические страницы).

## Частота ISR/регенерации
- Базовые страницы (лендинг, escrow, FAQ) – `24h`.
- Категории/скиллы – `12h` (ручные апдейты по данным каталогов).
- Блог – `6h` (чтобы забирать свежие публикации и комментарии).
- Публичные профили – `weekly` (в профиль попадают верифицированные изменения).
- Юридические страницы – `monthly`.
Настройки описаны в `frontend/ssg.config.mjs` и применяются в генераторе `frontend/scripts/prerender.mjs`.
