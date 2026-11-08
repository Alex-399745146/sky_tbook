# 📚 Sky TBook

[![CI](https://github.com/Alex-399745146/sky_tbook/actions/workflows/ci.yaml/badge.svg?branch=develop)](https://github.com/Alex-399745146/sky_tbook/actions/workflows/ci.yaml)
[![codecov](https://codecov.io/gh/Alex-399745146/sky_tbook/branch/develop/graph/badge.svg)](https://codecov.io/gh/Alex-399745146/sky_tbook)
![Python](https://img.shields.io/badge/python-3.13-blue)
![Django](https://img.shields.io/badge/django-4.2-092E20)
![DRF](https://img.shields.io/badge/DRF-3.17-A30000)
![PostgreSQL](https://img.shields.io/badge/postgresql-16-336791)

LMS-платформа: курсы и уроки, кастомные пользователи, платежи, подписки
и email-уведомления. REST API на Django REST Framework, веб-интерфейс на
Django-шаблонах и Bootstrap 5, фоновая обработка через Celery.

## 🚀 Возможности

- Курсы и уроки с владельцем и вложенным списком уроков.
- Кастомный пользователь с авторизацией по email.
- JWT-аутентификация (access + refresh).
- Ролевой доступ: владелец объекта, модератор, обычный пользователь.
- Подписка на курс и рассылка писем подписчикам при обновлении курса.
- Платежи: наличные, перевод, Stripe Checkout.
- Автоматическая деактивация пользователей, не входивших более месяца.
- OpenAPI-схема, Swagger UI и ReDoc.
- Веб-интерфейс: каталог, карточка курса, подписка, профиль, платежи.
- CRUD курсов и уроков через веб-формы с проверкой прав.
- 102 теста, покрытие 94%.

## 📸 Скриншоты

Каталог курсов:

![Каталог курсов](docs/screenshots/ui_home.png)

Карточка курса с уроками и действиями владельца:

![Карточка курса](docs/screenshots/ui_course_manage.png)

Личный кабинет с платежами:

![Платежи](docs/screenshots/ui_payments.png)

Создание курса:

![Форма курса](docs/screenshots/ui_course_form.png)

Swagger UI, ReDoc и админка Django:

![Swagger UI](docs/screenshots/swagger.png)

![ReDoc](docs/screenshots/redoc.png)

![Админка](docs/screenshots/admin_courses.png)

## 🖥️ Веб-интерфейс

- `/` — каталог курсов с поиском и пагинацией.
- `/courses/<id>/` — курс, уроки, подписка и доступ к видео.
- `/courses/new/`, `/courses/<id>/edit/`, `/courses/<id>/delete/` — CRUD курса.
- `/lessons/new/`, `/lessons/<id>/edit/`, `/lessons/<id>/delete/` — CRUD урока.
- `/login/`, `/register/`, `/logout/` — сессионная авторизация Django.
- `/profile/` — редактирование профиля и аватара.
- `/payments/` — свои платежи; модератор видит все.
- `/docs/` — ссылки на Swagger UI, ReDoc и OpenAPI JSON.

API и веб-интерфейс работают параллельно: DRF использует JWT, а браузерные
страницы — обычные Django-сессии и CSRF-защиту. Права проверяются на сервере
теми же функциями, что и в API.

## 🧰 Стек

| Слой | Технологии |
|---|---|
| Язык | Python 3.13 |
| Web | Django 4.2, Django REST Framework 3.17, Bootstrap 5 |
| База данных | PostgreSQL 16 |
| Аутентификация | Simple JWT |
| Фоновые задачи | Celery, Redis, django-celery-beat, django-celery-results |
| Платежи | Stripe API |
| Документация | drf-spectacular (OpenAPI, Swagger, ReDoc) |
| Инфраструктура | Docker, Docker Compose, Poetry |
| Качество кода | pytest, coverage, black, isort, flake8, mypy |

## 🗂️ Схема данных

```mermaid
erDiagram
    USER ||--o{ COURSE : "владеет"
    USER ||--o{ LESSON : "владеет"
    USER ||--o{ PAYMENT : "оплачивает"
    USER ||--o{ SUBSCRIPTION : "подписан"
    COURSE ||--o{ LESSON : "содержит"
    COURSE ||--o{ SUBSCRIPTION : "имеет"
    COURSE ||--o{ PAYMENT : "оплачен"
    LESSON ||--o{ PAYMENT : "оплачен"

    USER {
        int id
        string email
        string phone
        string city
        bool is_active
    }
    COURSE {
        int id
        string name
        text description
        int owner_id
    }
    LESSON {
        int id
        string name
        string video_url
        int course_id
        int owner_id
    }
    SUBSCRIPTION {
        int id
        int user_id
        int course_id
        datetime created_at
    }
    PAYMENT {
        int id
        decimal amount
        string payment_method
        int user_id
        int paid_course_id
        int paid_lesson_id
        string payment_url
    }
```

## 🛠️ Быстрый старт

### Docker Compose

```bash
git clone https://github.com/Alex-399745146/sky_tbook.git
cd sky_tbook
cp .env.docker.example .env.docker
# отредактируйте .env.docker: SECRET_KEY, DB_PASSWORD, ключи Stripe и почты
docker compose --env-file .env.docker up --build
```

Приложение будет доступно на `http://localhost:8000/`, Swagger — на
`http://localhost:8000/api/schema/swagger/`.

### Локально

Требуются Python 3.13, Poetry, PostgreSQL и Redis.

```bash
git clone https://github.com/Alex-399745146/sky_tbook.git
cd sky_tbook
poetry install
cp .env.example .env
# укажите в .env параметры PostgreSQL, Redis и SECRET_KEY
poetry run python manage.py migrate
poetry run python manage.py createsuperuser
poetry run python manage.py loaddata users/fixtures/groups.json
poetry run python manage.py runserver
```

Celery worker и Beat запускаются отдельными процессами:

```bash
poetry run celery -A config worker -P solo --loglevel=info
poetry run celery -A config beat --loglevel=info
```

Расписание задачи деактивации неактивных пользователей создаётся командой:

```bash
poetry run python manage.py setup_deactivate_inactive_users_task
```

## ⚙️ Переменные окружения

| Переменная | Назначение | Пример |
|---|---|---|
| `SECRET_KEY` | Ключ Django | длинная случайная строка |
| `DEBUG` | Режим отладки | `False` |
| `ALLOWED_HOSTS` | Разрешённые хосты через запятую | `localhost,127.0.0.1` |
| `DB_NAME` | Имя базы | `sky_tbook` |
| `DB_USER` | Пользователь БД | `sky_user` |
| `DB_PASSWORD` | Пароль БД | — |
| `DB_HOST` | Хост БД | `localhost` / `db` в Docker |
| `DB_PORT` | Порт БД | `5432` |
| `REDIS_URL` | Брокер Celery | `redis://127.0.0.1:6379/0` |
| `STRIPE_PUBLISHABLE_KEY` | Публичный ключ Stripe | `pk_test_...` |
| `STRIPE_SECRET_KEY` | Секретный ключ Stripe | `sk_test_...` |
| `EMAIL_HOST` | SMTP-сервер | `smtp.gmail.com` |
| `EMAIL_PORT` | Порт SMTP | `587` |
| `EMAIL_HOST_USER` | Логин SMTP | — |
| `EMAIL_HOST_PASSWORD` | Пароль приложения SMTP | — |

`.env`, `.env.docker` и файлы с реальными ключами в репозиторий не попадают.

## 🌍 API

| Раздел | Эндпоинты |
|---|---|
| Документация | `GET /api/schema/`, `/api/schema/swagger/`, `/api/schema/redoc/` |
| JWT | `POST /api/token/`, `POST /api/token/refresh/` |
| Регистрация | `POST /app_users/users/register/` |
| Пользователи | `GET/PUT/PATCH/DELETE /app_users/users/{id}/` |
| Курсы | `GET/POST /app_materials/courses/`, `GET/PUT/PATCH/DELETE /app_materials/courses/{id}/` |
| Уроки | `GET /app_materials/lessons/`, `POST /app_materials/lessons/create/`, `GET/PUT/PATCH/DELETE /app_materials/lessons/{id}/` |
| Подписка | `POST /app_materials/course/{id}/subscribe/` |
| Платежи | `GET /app_users/payments/`, `POST /app_users/payments/create/` |

Списки курсов, уроков, пользователей и платежей пагинированы:
`?page=1&page_size=10` (максимум `page_size=20`). Платежи фильтруются по
`paid_course`, `paid_lesson`, `payment_method`, сортируются по `payment_date` и
`amount`, поиск — по email пользователя.

## 🛡️ Права доступа

| Действие | Обычный пользователь | Владелец объекта | Модератор |
|---|---|---|---|
| Каталог курсов и уроков | ✅ | ✅ | ✅ |
| Создать курс или урок | ✅ | ✅ | ❌ |
| Редактировать свой объект | ❌ | ✅ | ✅ |
| Редактировать чужой объект | ❌ | ❌ | ✅ |
| Удалить свой объект | ❌ | ✅ | ❌ |
| Удалить чужой объект | ❌ | ❌ | ❌ |
| Список пользователей | ❌ | ❌ | ✅ |
| Свой профиль | ✅ | ✅ | ✅ |
| Чужой профиль | ❌ | ❌ | ✅ |
| Свои платежи | ✅ | ✅ | ✅ |
| Все платежи | ❌ | ❌ | ✅ |

Модератор — суперпользователь или участник группы `moderators`.

## ✅ Тесты

```bash
poetry run pytest
```

- 102 теста: регистрация, JWT, роли, права владельца и модератора,
  платежи, подписки, email-уведомления, страницы и CRUD веб-интерфейса.
- Покрытие — **94%** (`pytest --cov`, без миграций и самих тестов).
- Тесты используют SQLite и eager-режим Celery, внешние сервисы замоканы.

CI (`.github/workflows/ci.yaml`) запускает black, isort, flake8, mypy, тесты
и загружает coverage в Codecov. Сборка Docker-образа выполняется после
успешного lint и test.

## 🚢 Деплой

Workflow `.github/workflows/deploy.yaml` готов к работе, но запускается
**только вручную** (`workflow_dispatch`): демо-сервер выключен, автоматический
деплой при пуше отключён. Для запуска нужны секреты репозитория:

`SSH_HOST`, `SSH_USER`, `SSH_PRIVATE_KEY`, `SSH_PORT`, `SECRET_KEY`, `DEBUG`,
`ALLOWED_HOSTS`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`,
`REDIS_URL`, `STRIPE_PUBLISHABLE_KEY`, `STRIPE_SECRET_KEY`, `EMAIL_HOST`,
`EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`.

Перед миграциями workflow заново создаёт `.env` на сервере из этих секретов,
поэтому значения не остаются устаревшими после ротации. Переменная `APP_URL`
(Settings → Variables) включает healthcheck.

## ✍️ Автор

**Александр Бачевский** — Python-разработчик (backend, Django/DRF).

- GitHub: [Alex-399745146](https://github.com/Alex-399745146)
- Email: bachevskiiaa@gmail.com
