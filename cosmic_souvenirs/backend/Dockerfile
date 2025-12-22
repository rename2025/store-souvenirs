FROM python:3.13-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    python3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Копирование зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Создание пользователя ПОСЛЕ установки зависимостей
RUN useradd -m -u 1000 webuser

# Создание директорий с правами webuser
RUN mkdir -p /app/media/categories /app/staticfiles && \
    chown -R webuser:webuser /app/media /app/staticfiles && \
    chmod -R 755 /app/media

# Копирование проекта ПОСЛЕ смены владельца
COPY --chown=webuser:webuser . .

# Копирование и настройка entrypoint
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Переключаемся на webuser
USER webuser

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "cosmic_souvenirs.wsgi:application", "--bind", "0.0.0.0:8000"]
