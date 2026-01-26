#  Cosmic Souvenirs 
## Космический магазин с промокодами и аналитикой

![Django](https://img.shields.io/badge/Django-5.0-green) 
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-blue) 
![Docker](https://img.shields.io/badge/Docker-Compose-orange) 
![Python](https://img.shields.io/badge/Python-3.13-yellow)

**Полнофункциональный e-commerce с 🔥 промокодами (высокий ROI) и 📊 админ-дашбордом**

## ✨ Ключевые фичи
### 🛒 Магазин
- ✅ Каталог с фильтрами/категориями
- ✅ Корзина + **Промокоды** (%/₽, срок действия, лимит)
- ✅ YooKassa оплата
- ✅ Отзывы/рейтинги
- ✅ Поиск товаров

### 👑 Админ-дашборд
- 📈 Мониторинг заказов
- 💰 Аналитика продаж
- 🎫 Управление промокодами
- 👥 Пользователи/отзывы

## ⚡ Быстрый старт
```bash
git clone https://github.com/rename2025/store-souvenirs
cd store-souvenirs
docker-compose up -d

Django 5.0 + DRF    # Бэкенд
PostgreSQL 17       # БД
Redis + Celery      # Кеш/задачи
Docker Compose      # Контейнеры
Bootstrap 5         # Фронтенд

✔ redis      # ✅ Healthy
✔ postgres   # ✅ Healthy  
✔ web        # Gunicorn 8000
✔ nginx      # localhost:80
✔ celery     # Задачи
✔ celery-beat# Планировщик

📄 Лицензия
MIT © 2026