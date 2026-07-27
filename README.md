sky_tbook
Учебный Django‑проект LMS (Learning Management System) с API на Django REST Framework и фоновыми задачами через Celery.

Основной функционал
Курсы и уроки (Course, Lesson) с владельцем (owner) и вложенным списком уроков.

Кастомный пользователь по email, профиль, платежи (Payment).

JWT‑аутентификация (Simple JWT), роли через группу moderators, пермишены IsModer и IsOwner.

Подписка на обновления курса (Subscription) и рассылка писем подписчикам при обновлении курса (Celery‑задача).

Периодическая задача через django‑celery‑beat, которая раз в день ищет пользователей с last_login старше месяца и отключает их (is_active = False).

Стек
Python 3.13, Django 4.2, DRF 3.17

PostgreSQL

Redis (broker/backend для Celery)

Celery, django‑celery‑results, django‑celery‑beat

djangorestframework‑simplejwt, Pillow, python‑dotenv

Установка и запуск
bash
git clone https://github.com/Alex-399745146/sky_tbook.git
cd sky_tbook

poetry install
poetry run python manage.py migrate
poetry run python manage.py loaddata users/fixtures/groups.json
poetry run python manage.py createsuperuser

# сервер
poetry run python manage.py runserver

# Celery (Windows)
poetry run celery -A config worker -P solo --loglevel=info
poetry run celery -A config beat --loglevel=info
Redis должен быть запущен локально на redis://127.0.0.1:6379/0.

Кратко по API
JWT: POST /api/token/, POST /api/token/refresh/.

Пользователи: CRUD под /app_users/users/, регистрация /register/.

Курсы: /app_materials/courses/ (CRUD, вложенные уроки).

Уроки: /app_materials/lessons/.

Подписки на курс: эндпоинт toggle‑подписки, рассылка писем при обновлении курса.

Платежи: /app_users/payments/ с фильтрами по курсу/уроку и способу оплаты.