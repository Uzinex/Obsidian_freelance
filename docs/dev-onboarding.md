# Onboarding нового разработчика

Следуйте шагам ниже, чтобы подготовить окружение и запустить проект Obsidian Freelance локально.

## 1. Клонирование репозитория
```bash
git clone git@github.com:your-org/obsidian-freelance.git
cd obsidian-freelance
```
> При необходимости замените URL на HTTPS-версию.

## 2. Установка Python и Node.js
- Python 3.12 или выше
- Node.js 20 или выше (вместе с npm)

Проверьте версии:
```bash
python --version
node --version
```

## 3. Создание и активация виртуального окружения Python
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
```

## 4. Установка зависимостей
```bash
pip install -r requirements.txt
cd ../frontend
npm install
```

## 5. Настройка переменных окружения
1. Вернитесь в корень репозитория.
2. Скопируйте шаблон `.env.example` (или актуальный файл из `docs/env-variables.md`) в `.env`.
3. Заполните значения по инструкции из [docs/env-setup.md](env-setup.md).

## 6. Применение миграций и сидов
```bash
cd backend
python manage.py migrate
python manage.py loaddata seeds/*  # при наличии файлов сидов
```

## 7. Запуск backend и frontend
В отдельных терминалах запустите:
```bash
# Backend
cd backend
source .venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```
```bash
# Frontend
cd frontend
npm run dev -- --host 0.0.0.0 --port 5173
```

После запуска backend доступен на `http://localhost:8000`, frontend — на `http://localhost:5173`.
