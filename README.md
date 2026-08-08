# Sky TBook API 🚀

Учебный DRF-проект: платформа для продажи курсов и уроков с подписками и оплатой через Stripe.

## Особенности

- ✅ **Django 4.2 + DRF** — REST API с JWT-аутентификацией
- ✅ **PostgreSQL 16** — надёжная база данных
- ✅ **Celery + Redis** — фоновые задачи и периодические задачи
- ✅ **Stripe** — оплата подписок и курсов
- ✅ **Docker** — полная контейнеризация для разработки и деплоя
- ✅ **drf-spectacular** — автоматическая документация API

## Технологии

| Технология | Версия | Назначение |
|------------|--------|------------|
| Python | 3.13 | Основной язык |
| Django | 4.2 | Веб-фреймворк |
| Django REST Framework | 3.17 | REST API |
| PostgreSQL | 16 | База данных |
| Redis | 7 | Брокер сообщений для Celery |
| Celery | 5.6 | Фоновые задачи |
| Docker | latest | Контейнеризация |

## Быстрый старт

### Требования

- Docker и Docker Compose
- Python 3.13 (для локальной разработки)

### Запуск через Docker

```bash
# Клонируй репозиторий
git clone https://github.com/Alex-399745146/sky_tbook.git
cd sky_tbook

# Создай .env файл с реальными секретами
cp .env.example .env
# Отредактируй .env, вставь свои ключи Stripe и email

# Запусти все сервисы
docker compose up
```

Сервисы будут доступны:
- **Django API**: http://localhost:8000
- **Документация API**: http://localhost:8000/api/docs/
- **Админка**: http://localhost:8000/admin

### Локальная разработка (без Docker)

```bash
# Установи зависимости
pip install -r requirements.txt

# Создай .env файл
cp .env.example .env

# Запусти миграции
python manage.py migrate

# Создай суперпользователя
python manage.py createsuperuser

# Запусти сервер
python manage.py runserver
```

## Структура проекта
