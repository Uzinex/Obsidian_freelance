# Политика Content Security Policy

## Директивы по умолчанию
- `default-src 'self'`
- `script-src 'self' https://cdn.obsidian.io`
- `style-src 'self' https://fonts.googleapis.com`
- `font-src 'self' https://fonts.gstatic.com`
- `img-src 'self' data: https://cdn.obsidian.io`
- `connect-src 'self'` плюс API-origin из белого списка CORS
- `frame-ancestors 'none'`

## Примечания
- Любые новые сторонние CDN должны быть явно добавлены в CSP и задокументированы.
- Inline-скрипты запрещены. Для интеграций, требующих inline-инициализации, используйте `nonce`-механику (нужно добавить в middleware).
- Для загрузок через presigned URL выставляется заголовок `X-Content-Type-Options: nosniff`, чтобы браузер не выполнял контент.
- CSP применяется глобально через `SecurityHeadersMiddleware`, ответ может переопределить директивы только в исключительных случаях (например, при выдаче файлов).
