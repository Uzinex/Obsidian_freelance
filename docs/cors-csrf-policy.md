# Политика CORS и CSRF

## Допустимые origin
| Среда | CORS origin | Cookies / CSRF |
| --- | --- | --- |
| Dev | `http://localhost:3000`, `http://127.0.0.1:3000`, `http://localhost:5173`, `http://127.0.0.1:5173` | CSRF-токены выдаются только при HTTPS отсутствует, поэтому режим разработки допускает HTTP origin; cookies имеют SameSite=Lax |
| Stage | `https://stage.app.obsidian.dev`, `https://stage-admin.obsidian.dev` | Требуется HTTPS. Origins автоматически добавляются в список доверенных для CSRF. |
| Prod | `https://app.obsidian.io`, `https://admin.obsidian.io` | Требуется HTTPS, строгий контроль CORS; CSRF-токены выдаются только этим origin. |

Произвольные `*` и динамические origin запрещены. Расширение списка возможно только через `DJANGO_CORS_ALLOWED_ORIGINS` в конфиге, с обязательным ревью безопасности.

## Правила
- Куки авторизации (`sessionid`, JWT refresh) настроены с `Secure`, `HttpOnly`, `SameSite=Lax` и ограниченным временем жизни (8 часов по умолчанию).
- CSRF-cookie также имеет `Secure`, `HttpOnly`, `SameSite=Lax` и TTL 8 часов.
- Все небезопасные методы (POST/PUT/PATCH/DELETE) требуют валидного CSRF-токена, если запрос содержит cookie. Проверка выполняется стандартным `CsrfViewMiddleware` и дополнительной проверкой в `RoleBasedAccessPermission` при работе через сессии.
- Доверенные origin для CSRF — только HTTPS-значения из белого списка.
- Куки и токены не выдаются на нестандартные поддомены без отдельного изменения настроек.
