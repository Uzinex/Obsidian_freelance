# Analytics Events v0

Набор базовых событий аналитики для платформы Obsidian Freelance.

## Сводная таблица событий

| Событие | Бизнесовое значение | Ключевые свойства |
| --- | --- | --- |
| `user_registered` | Пользователь успешно завершил регистрацию и подтвердил создание учётной записи. | `user_role` — выбранная роль (freelancer, client); `registration_method` — способ регистрации (email, oauth и т.д.); `traffic_source` — UTM-источник/кампания; `interface_language` — язык интерфейса при регистрации; `device_type` — desktop/mobile/tablet. |
| `order_created` | Заказчик опубликовал новый заказ и сделал его доступным на витрине. | `client_role_level` — тип клиента (new, returning, verified); `order_category` — основная категория заказа; `order_type` — формат (fixed_price, hourly, milestone); `budget_amount` и `budget_currency`; `deadline_type` — фиксированный срок/гибкий; `skills_count` — число выбранных навыков. |
| `order_responded` | Фрилансер отправил отклик на заказ. | `freelancer_experience_level` — junior/middle/senior; `order_category`; `proposal_type` — стандартный/быстрый отклик; `response_time_sec` — время с момента публикации заказа; `has_cover_letter` — флаг наличия сопроводительного письма. |
| `contract_started` | Заказчик и фрилансер подтвердили старт работы над заказом. | `contract_type` — fixed_price/hourly; `order_category`; `agreed_budget_amount` и `agreed_budget_currency`; `start_trigger` — manual/auto (например, автопринятие после депозита); `escrow_enabled` — флаг наличия эскроу. |
| `contract_completed` | Работа завершена и контракт закрыт (успешно или нет). | `completion_status` — success/cancelled/disputed; `total_paid_amount` и `currency`; `work_duration_days`; `client_rating` и `freelancer_rating`; `has_review` — оставлен ли отзыв. |

## Рекомендации по интеграции на фронтенде

- **`user_registered`** — отправлять после успешного ответа API на форму регистрации (`/register`), в месте, где уже показано подтверждение пользователю.
- **`order_created`** — логировать сразу после получения успешного ответа от API создания заказа в мастере/форме публикации заказа.
- **`order_responded`** — вызывать после успешной отправки отклика фрилансером (форма предложения / кнопка «Откликнуться»).
- **`contract_started`** — фиксировать при подтверждении обеих сторон: например, после страницы подтверждения контракта или модального окна старта работы.
- **`contract_completed`** — отправлять после подтверждения закрытия заказа (кнопка «Завершить»/«Работа выполнена») и получения успешного ответа API.

При реализации необходимо убедиться, что события отправляются один раз и после подтверждения API, чтобы избежать двойного подсчёта.
