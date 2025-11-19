# Obsidian Freelance

Obsidian Freelance — fullstack-платформа для фрилансеров и заказчиков, помогающая искать проекты, управлять задачами и поддерживать коммуникацию между сторонами.

## Технологический стек
- Backend: Django, Django REST Framework, PostgreSQL
- Frontend: React, Vite

## Быстрый старт
### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py loaddata seeds/*  # при наличии сидов
python manage.py runserver 0.0.0.0:8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 5173
```

### reCAPTCHA и Google OAuth
Для рабочей регистрации необходимо задать ключи в переменных окружения:

- `RECAPTCHA_SECRET_KEY` и `VITE_RECAPTCHA_SITE_KEY` — пара ключей Google reCAPTCHA v3.
- `GOOGLE_OAUTH_CLIENT_ID` и `VITE_GOOGLE_CLIENT_ID` — OAuth Client ID для кнопок «Войти/Зарегистрироваться с Google».

Письма с кодом подтверждения отправляются с адреса `obsidianfreelance@gmail.com`. При необходимости переопределите его через `DEFAULT_FROM_EMAIL`.

## Документация
Расширенные инструкции расположены в каталоге [docs/](docs/).
