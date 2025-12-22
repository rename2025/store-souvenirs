# 🚨 PRODUCTION SETTINGS - ЗАМЕНИТЕ ВСЕ НА СВОИ ДАННЫЕ

import os
from .settings import *

# Безопасность
DEBUG = False
ALLOWED_HOSTS = [
    '🚨-cosmic-souvenirs.ru',
    '🚨-www.cosmic-souvenirs.ru',
    '🚨-IP-АДРЕС-СЕРВЕРА',
]

# 🗄️ Production Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB', '🚨-PROD-DB-NAME'),
        'USER': os.getenv('POSTGRES_USER', '🚨-PROD-DB-USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', '🚨-PROD-DB-PASSWORD'),
        'HOST': os.getenv('POSTGRES_HOST', '🚨-PROD-DB-HOST'),
        'PORT': os.getenv('POSTGRES_PORT', '5432'),
        'CONN_MAX_AGE': 600,
        'OPTIONS': {
            'sslmode': 'require',
        }
    }
}

# 📧 Production Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = '🚨-smtp.yandex.ru'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = '🚨-noreply@cosmic-souvenirs.ru'
EMAIL_HOST_PASSWORD = '🚨-ПАРОЛЬ-ПРИЛОЖЕНИЯ'
DEFAULT_FROM_EMAIL = '🚨-noreply@cosmic-souvenirs.ru'

# 💳 Real YooKassa credentials
YOOKASSA_SHOP_ID = '🚨-REAL-SHOP-ID'
YOOKASSA_SECRET_KEY = '🚨-REAL-SECRET-KEY'