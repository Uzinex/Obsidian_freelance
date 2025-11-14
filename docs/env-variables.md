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
