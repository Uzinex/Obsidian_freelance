# Карта публичных URL (uz/ru)

| Раздел | Описание | uz путь | ru путь | Тип генерации |
| --- | --- | --- | --- | --- |
| Главная | Лендинг с value prop, CTA | `/uz/` | `/ru/` | SSG (build-time) |
| Как работает | Шаги использования платформы | `/uz/qanday-ishlaydi` | `/ru/kak-rabotaet` | SSG |
| Escrow | Механика безопасных сделок | `/uz/escrow` | `/ru/escrow` | SSG |
| Стоимость и комиссии | Тарифы, комиссии, расчёты | `/uz/narxlar` | `/ru/stoimost` | SSG |
| Для заказчиков | Польза и фичи для клиентов | `/uz/zakazchilar` | `/ru/zakazchiki` | SSG |
| Для исполнителей | Польза и фичи для фрилансеров | `/uz/ijrochilar` | `/ru/ispolniteli` | SSG |
| Каталог профилей | Публичная витрина фрилансеров с фильтрами | `/uz/profillar` | `/ru/profiles` | ISR (revalidate 60с) |
| Профиль фрилансера | Публичный профиль `{userSlug}` | `/uz/profillar/{userSlug}` | `/ru/profiles/{userSlug}` | ISR on-demand |
| Каталог проектов | Открытые проекты/вакансии | `/uz/loyihalar` | `/ru/proekty` | ISR (revalidate 60с) |
| Проект детали | Детали конкретного проекта `{projectSlug}` | `/uz/loyihalar/{projectSlug}` | `/ru/proekty/{projectSlug}` | ISR on-demand |
| Кейсы и истории успеха | Подборки кейсов | `/uz/keyslar` | `/ru/keisy` | SSG |
| Блог / статьи | Контентный блог (если есть) | `/uz/blog` | `/ru/blog` | ISR (revalidate по публикации) |
| Контакты и поддержка | Контактная информация | `/uz/kontaktlar` | `/ru/kontakty` | SSG |
| FAQ | Ответы на вопросы по escrow/платформе | `/uz/savollar` | `/ru/faq` | SSG |

Примечания:
- Любой новый публичный маршрут создаётся в формате `/{locale}/slug` с локализованным slug-ом, если это контентная страница.
- Динамические сегменты (`{userSlug}`, `{projectSlug}`) не переводятся.
- Для старых URL без локали настраивается 301 редирект на соответствующий путь (например, `/escrow` → `/uz/escrow`).
