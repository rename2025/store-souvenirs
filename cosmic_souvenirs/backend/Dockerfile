FROM python:3.13-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    python3-dev \
    curl \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копирование и установка зависимостей (кэшируется)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Создание пользователя и директорий
RUN useradd -m -u 1000 webuser && \
    mkdir -p /app/media/categories /app/staticfiles && \
    chown -R webuser:webuser /app/media /app/staticfiles && \
    chmod -R 755 /app/media

# Копирование проекта
COPY --chown=webuser:webuser . .

# Переключаемся на webuser
USER webuser

EXPOSE 8000

# УБРАЛ entrypoint.sh - используем command из docker-compose.yml
CMD ["gunicorn", "cosmic_souvenirs.wsgi:application", "--bind", "0.0.0.0:8000"]
