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

## Документация
Расширенные инструкции расположены в каталоге [docs/](docs/).
