# Environment Variables

| NAME | SERVICE | TYPE | REQUIRED | DEFAULT | DESCRIPTION |
| --- | --- | --- | --- | --- | --- |
| `DJANGO_SECRET_KEY` | backend | str | да | `django-insecure-…` (только для разработки) | Секретный ключ Django, используется для криптографии и подписей. |
| `DJANGO_DEBUG` | backend | bool | нет | `True` | Управляет режимом отладки Django. Отключайте в продакшене. |
| `DJANGO_ALLOWED_HOSTS` | backend | list[str] | нет | `*` | Список хостов, с которых разрешены запросы к бэкенду. |
| `DATABASE_URL` | backend | URL | да | — | Строка подключения к основной базе данных PostgreSQL. |
| `DJANGO_CORS_ALLOWED_ORIGINS` | backend | list[URL] | нет | `http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173` | Разрешённые источники для CORS. |
| `DJANGO_CORS_ALLOW_CREDENTIALS` | backend | bool | нет | `True` | Управляет передачей cookie/заголовков авторизации в CORS-запросах. |
| `VERIFICATION_ADMIN_EMAIL` | backend | email | да | _(пусто)_ | Email аккаунта, уполномоченного утверждать заявки на верификацию. |
| `VITE_API_BASE_URL` | frontend | URL | да | `http://localhost:8000` | Базовый URL API, к которому обращается фронтенд. |
| `VITE_VERIFICATION_ADMIN_EMAIL` | frontend | email | да | _(пусто)_ | Email проверяющего администратора, используемый на клиенте для отображения прав. |
| `JWT_ENVIRONMENT` | backend | str | нет | `dev` | Активный набор ключей (`dev`, `stage`, `prod`). |
| `JWT_ACCESS_TTL_SECONDS` | backend | int | нет | `600` | Срок жизни access-токена в секундах (5–10 минут). |
| `JWT_REFRESH_TTL_SECONDS` | backend | int | нет | `2419200` | Срок жизни refresh-токена при выдаче (28 дней). |
| `JWT_REFRESH_SLIDING_WINDOW_SECONDS` | backend | int | нет | `1209600` | Длительность «скользящего окна» для ротации refresh-токена (14 дней). |
| `JWT_REFRESH_ABSOLUTE_LIFETIME_SECONDS` | backend | int | нет | `2592000` | Максимальная абсолютная жизнь refresh-токена (30 дней). |
| `JWT_REFRESH_COOKIE_NAME` | backend | str | нет | `refresh_token` | Имя cookie, в которой хранится refresh. |
| `JWT_REFRESH_COOKIE_PATH` | backend | str | нет | `/` | Путь cookie refresh. |
| `JWT_REFRESH_COOKIE_SECURE` | backend | bool | нет | `True` | Принудительное выставление cookie как Secure. |
| `JWT_REFRESH_COOKIE_SAMESITE` | backend | str | нет | `Strict` | Политика SameSite для refresh cookie. |
| `JWT_ACCESS_DEV_KID` | backend | str | да (Dev) | _(пусто)_ | Идентификатор ключа access для Dev. |
| `JWT_ACCESS_DEV_PRIVATE_KEY` | backend | str (PEM) | да (Dev) | _(пусто)_ | Приватный ключ access Dev. |
| `JWT_ACCESS_DEV_PUBLIC_KEY` | backend | str (PEM) | да (Dev) | _(пусто)_ | Публичный ключ access Dev. |
| `JWT_ACCESS_DEV_ALGORITHM` | backend | str | нет | `RS256` | Алгоритм подписи access Dev. |
| `JWT_REFRESH_DEV_KID` | backend | str | да (Dev) | _(пусто)_ | Идентификатор refresh ключа Dev. |
| `JWT_REFRESH_DEV_PRIVATE_KEY` | backend | str (PEM) | да (Dev) | _(пусто)_ | Приватный ключ refresh Dev. |
| `JWT_REFRESH_DEV_PUBLIC_KEY` | backend | str (PEM) | да (Dev) | _(пусто)_ | Публичный ключ refresh Dev. |
| `JWT_REFRESH_DEV_ALGORITHM` | backend | str | нет | `RS256` | Алгоритм подписи refresh Dev. |
| `JWT_ACCESS_STAGE_KID` | backend | str | да (Stage) | _(пусто)_ | Идентификатор ключа access для Stage. |
| `JWT_ACCESS_STAGE_PRIVATE_KEY` | backend | str (PEM) | да (Stage) | _(пусто)_ | Приватный ключ access Stage. |
| `JWT_ACCESS_STAGE_PUBLIC_KEY` | backend | str (PEM) | да (Stage) | _(пусто)_ | Публичный ключ access Stage. |
| `JWT_ACCESS_STAGE_ALGORITHM` | backend | str | нет | `RS256` | Алгоритм подписи access Stage. |
| `JWT_REFRESH_STAGE_KID` | backend | str | да (Stage) | _(пусто)_ | Идентификатор refresh ключа Stage. |
| `JWT_REFRESH_STAGE_PRIVATE_KEY` | backend | str (PEM) | да (Stage) | _(пусто)_ | Приватный ключ refresh Stage. |
| `JWT_REFRESH_STAGE_PUBLIC_KEY` | backend | str (PEM) | да (Stage) | _(пусто)_ | Публичный ключ refresh Stage. |
| `JWT_REFRESH_STAGE_ALGORITHM` | backend | str | нет | `RS256` | Алгоритм подписи refresh Stage. |
| `JWT_ACCESS_PROD_KID` | backend | str | да (Prod) | _(пусто)_ | Идентификатор ключа access для Prod. |
| `JWT_ACCESS_PROD_PRIVATE_KEY` | backend | str (PEM) | да (Prod) | _(пусто)_ | Приватный ключ access Prod. |
| `JWT_ACCESS_PROD_PUBLIC_KEY` | backend | str (PEM) | да (Prod) | _(пусто)_ | Публичный ключ access Prod. |
| `JWT_ACCESS_PROD_ALGORITHM` | backend | str | нет | `RS256` | Алгоритм подписи access Prod. |
| `JWT_REFRESH_PROD_KID` | backend | str | да (Prod) | _(пусто)_ | Идентификатор refresh ключа Prod. |
| `JWT_REFRESH_PROD_PRIVATE_KEY` | backend | str (PEM) | да (Prod) | _(пусто)_ | Приватный ключ refresh Prod. |
| `JWT_REFRESH_PROD_PUBLIC_KEY` | backend | str (PEM) | да (Prod) | _(пусто)_ | Публичный ключ refresh Prod. |
| `JWT_REFRESH_PROD_ALGORITHM` | backend | str | нет | `RS256` | Алгоритм подписи refresh Prod. |
| `JWT_ACCESS_ADDITIONAL_PUBLIC_KEYS` | backend | str | нет | _(пусто)_ | Keyring публичных ключей прошлых access `kid` (`kid::pub||...`). |
| `JWT_REFRESH_ADDITIONAL_PUBLIC_KEYS` | backend | str | нет | _(пусто)_ | Keyring публичных ключей прошлых refresh `kid`. |
| `FEATURE_AUTH_JWT` | backend | bool | нет | `False` | Включает JWT-аутентификацию. |
| `FEATURE_AUTH_TOKEN_LEGACY` | backend | bool | нет | `True` | Оставляет поддержку legacy токенов DRF. |
| `FEATURE_AUTH_2FA` | backend | bool | нет | `False` | Требовать 2FA при логине. |
| `FEATURE_UPLOAD_SCANNER` | backend | bool | нет | `False` | Включить сканер загрузок. |
| `FEATURE_ADMIN_HARDENING` | backend | bool | нет | `False` | Усиление безопасности админки. |
