# 📚 Sky TBook

Backend LMS-платформы для публикации курсов и учебных материалов. Сервис предоставляет REST API для управления курсами, уроками, пользователями, платежами и подписками. Клиентское приложение взаимодействует с сервером через JSON API.

## 🚀 Возможности

- Создание и управление курсами и уроками
- Привязка материалов к владельцу и вложенный список уроков в курсах
- Регистрация пользователей по email и управление профилем
- JWT-аутентификация
- Ролевой доступ: модераторы и владельцы объектов
- Подписка на обновления курсов и email-уведомления подписчиков
- Учёт платежей с фильтрацией по курсу, уроку и способу оплаты
- Фоновая обработка задач через Celery
- Автоматическая деактивация пользователей, которые не входили в систему более месяца

## 🧰 Технологии

- Python 3.13
- Django 4.2, Django REST Framework 3.17
- PostgreSQL
- Celery, Redis, django-celery-beat, django-celery-results
- Simple JWT
- Poetry

## 🛠️ Установка и запуск

### 📋 Требования

Установите Python, Poetry, PostgreSQL и Redis. Создайте базу данных PostgreSQL и подготовьте переменные окружения для подключения к ней и настройки приложения.

### 📥 Установка зависимостей

```bash
git clone [https://github.com/Alex-399745146/sky_tbook.git](https://github.com/Alex-399745146/sky_tbook.git)
cd sky_tbook
poetry install
```

Создайте файл `.env` и укажите в нём параметры приложения и подключения к PostgreSQL, соответствующие настройкам проекта.

### 🗄️ Подготовка базы данных

```bash
poetry run python manage.py migrate
poetry run python manage.py createsuperuser
```

При наличии фикстур загрузите подготовленные данные:

```bash
poetry run python manage.py loaddata <путь-к-файлу-фикстуры>
```

### ▶️ Запуск Django-сервера

```bash
poetry run python manage.py runserver
```

## 🔄 Celery и Redis

Убедитесь, что Redis запущен и доступен по адресу `redis://127.0.0.1:6379/0`.

Запустите Celery worker и Celery Beat в отдельных терминалах:

```bash
poetry run celery -A config worker -P solo --loglevel=info
```

```bash
poetry run celery -A config beat --loglevel=info
```

Для настройки периодической задачи деактивации неактивных пользователей выполните:

```bash
poetry run python manage.py setup_deactivate_inactive_users_task
```

Задача проверяет поле `last_login` и деактивирует аккаунты пользователей, не входивших в систему более месяца.

## 🌍 Основные API-эндпоинты

| Раздел | Эндпоинты |
|---|---|
| 🔐 JWT-аутентификация | `POST /api/token/`, `POST /api/token/refresh/` |
| 👥 Пользователи | `/app_users/users/`, регистрация — `/app_users/users/register/` |
| 📚 Курсы | `/app_materials/courses/` |
| 📝 Уроки | `/app_materials/lessons/` |
| 💳 Платежи | `/app_users/payments/` |

Подписки на курсы управляются отдельным эндпоинтом переключения подписки. При обновлении курса подписчикам отправляются email-уведомления.

## 🛡️ Структура доступа

- 👤 **Владелец** управляет собственными объектами в рамках назначенных разрешений.
- 🧑‍⚖️ **Модератор** получает расширенные права через группу модераторов.
- 🔒 Для разграничения доступа используются `IsOwner` и `IsModer`.

## ✍️ Автор

Alex Bachevskiy  
Python-разработчик | Python - developer
