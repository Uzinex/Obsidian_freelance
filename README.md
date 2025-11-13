# Obsidian Freelance

Обновлённая fullstack-платформа **OBSIDIAN FREELANCE** на базе Django (REST API) и React (Vite) с поддержкой PostgreSQL.

## Структура репозитория

```
backend/   # Django-проект и REST API
frontend/  # Vite + React SPA
venv/      # Локальное виртуальное окружение Python (не попадает в git)
```

## Backend (Django)

### Требования
- Python 3.12+
- PostgreSQL (используется внешний Railway-инстанс)

### Настройка
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Переменная `DATABASE_URL` по умолчанию уже настроена на Railway-инстанс:
```
postgresql://postgres:QodMCrMqhbvgtMsxuOlgKBgoZpOWcABE@trolley.proxy.rlwy.net:30558/railway
```
> ⚠️ В среде выполнения могут действовать сетевые ограничения. Если подключение к удалённой БД недоступно, настройте собственный PostgreSQL и переопределите `DATABASE_URL`.

### Миграции и суперпользователь
```bash
python manage.py makemigrations
python manage.py migrate  # требуется доступ к PostgreSQL
python manage.py createsuperuser
```

### Запуск сервера
```bash
python manage.py runserver 0.0.0.0:8000
```

Основные API-эндпоинты:
- `/api/accounts/register/`, `/api/accounts/login/`, `/api/accounts/logout/`
- `/api/accounts/profiles/`, `/api/accounts/profiles/me/`
- `/api/accounts/verifications/`
- `/api/marketplace/orders/`, `/api/marketplace/categories/`, `/api/marketplace/skills/`
- `/api/marketplace/applications/`

## Frontend (React)

### Требования
- Node.js 20+

### Установка зависимостей
```bash
cd frontend
npm install
```

### Запуск dev-сервера
```bash
npm run dev
```
Приложение доступно по адресу `http://localhost:5173`. В `vite.config.js` настроен прокси на `http://localhost:8000`, поэтому Django-сервер должен работать одновременно.

### Сборка продакшн-версии
```bash
npm run build
npm run preview  # опционально, локальный предпросмотр
```

## Ключевые возможности
- Регистрация c никнеймом, e-mail (Gmail), паролем и годом рождения (16+).
- Обязательное заполнение расширенного профиля с выбором роли (фрилансер/заказчик) и детальной анкетой.
- Верификация документов (паспорт, ID, водительские права) с загрузкой изображений для админ-проверки.
- Каталог заказов с фильтрами по категориям/навыкам/типам заказа, просмотр детальной информации и отклики фрилансеров.
- Каталог фрилансеров с фильтром по навыкам.
- Создание заказов заказчиками с настройкой дедлайна, бюджета, требуемых навыков и типа заказа.
- Предзаполненные категории и навыки согласно ТЗ (маркетинг, дизайн, программирование и др.).
- REST API с токен-авторизацией (`rest_framework.authtoken`).
- Frontend SPA с хранением токена и разделением доступа (ProtectedRoute).

## Известные ограничения
- Доступ к удалённой БД Railway может быть ограничен внутри контейнера (ошибка `Network is unreachable`). Для работы локально поднимите свой PostgreSQL и обновите `DATABASE_URL`.
- При первом обращении к `/api/accounts/profiles/me/` создаётся черновой профиль с ролью "заказчик" — её можно изменить в форме профиля.

## Скриншоты логотипа
Логотип расположен в `frontend/public/logo.svg` и используется на всех страницах SPA.
