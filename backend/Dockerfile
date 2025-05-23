FROM python:3.13-alpine

# Переменные окружения
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY data/ingredients.json .

COPY backend/requirements.txt .

RUN pip install -r requirements.txt --no-cache-dir

COPY backend .

# Сборка статики и миграции при запуске
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --no-input && gunicorn --bind 0.0.0.0:8000 backend.wsgi"]
