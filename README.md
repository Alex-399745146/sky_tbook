# sky_tbook

Учебный Django‑проект LMS (Learning Management System) для онлайн‑курсов с API на Django REST Framework [web:102].

## Описание

Проект реализует базовый функционал LMS:

- управление курсами и уроками;
- вложенный вывод уроков внутри курса (количество и список);
- работа с пользователями и их профилями;
- учёт платежей за курсы и отдельные уроки.

## Технологии

- Python 3.13
- Django 4.2
- Django REST Framework 3.17 [web:98]
- PostgreSQL
- Pillow (для работы с изображениями)
- python-dotenv

## Структура

Основные приложения:

- `app_materials` — курсы и уроки (`Course`, `Lesson`, сериализаторы с количеством и списком уроков, API).
- `app_users` — пользователи (кастомная модель `User` по email, профиль, модель `Payment` для оплат).

Главные файлы:

- `config/settings.py` — настройки проекта.
- `config/urls.py` — корневые маршруты.
- `app_materials/models.py` — модели `Course` и `Lesson`.
- `app_materials/serializers.py` — сериализаторы курсов и уроков (вложенные уроки и `lessons_count`).
- `app_materials/views.py` — ViewSet для `Course` и Generic‑вью для `Lesson`.
- `app_materials/urls.py` — маршруты API курсов и уроков.
- `app_users/models.py` — кастомный `User` и `Payment`.
- `app_users/serializers.py` — сериализатор `Payment`.
- `app_users/urls.py` — маршруты API пользователей и платежей.

## Установка и запуск

```bash
# клонировать репозиторий
git clone https://github.com/Alex-399745146/sky_tbook.git
cd sky_tbook

# установить зависимости через Poetry
poetry install

# применить миграции
poetry run python manage.py migrate

# запустить сервер разработки
poetry run python manage.py runserver
```

После запуска сервер будет доступен по адресу:
- `http://127.0.0.1:8000/`

## API эндпоинты

### Курсы (Course)

Базовый префикс: `/app_materials/`

- `GET /app_materials/courses/` — список курсов (с количеством уроков и вложенными уроками).
- `POST /app_materials/courses/` — создание курса.
- `GET /app_materials/courses/{id}/` — получить курс.
- `PUT /app_materials/courses/{id}/` — обновить курс.
- `PATCH /app_materials/courses/{id}/` — частично обновить курс.
- `DELETE /app_materials/courses/{id}/` — удалить курс.

### Уроки (Lesson)

- `GET /app_materials/lessons/` — список уроков.
- `POST /app_materials/lessons/create/` — создание урока.
- `GET /app_materials/lessons/{id}/` — получить урок.
- `PUT /app_materials/lessons/{id}/update/` — обновить урок.
- `DELETE /app_materials/lessons/{id}/delete/` — удалить урок.

### Платежи (Payment)

Базовый префикс: `/app_users/`

- `GET /app_users/payments/` — список платежей с фильтрацией и сортировкой:
  - `?ordering=asc|desc` — порядок по дате оплаты [web:104].
  - `?course={id}` — фильтр по курсу.
  - `?lesson={id}` — фильтр по уроку.
  - `?method=cash|transfer` — фильтр по способу оплаты.

## Проверка через Postman

1. Запусти сервер: `poetry run python manage.py runserver`.
2. В Postman создай коллекцию с запросами:
   - курсы: `GET/POST/PUT/PATCH/DELETE` на `/app_materials/courses/…`;
   - уроки: `GET/POST/PUT/DELETE` на `/app_materials/lessons/…`;
   - платежи: `GET` на `/app_users/payments/` с нужными query‑параметрами.
3. Используй `Content-Type: application/json` для `POST`, `PUT` и `PATCH`.

## Статус

Проект используется для выполнения домашних заданий по Django/DRF, постепенно расширяется функционалом LMS и интеграцией платежей [web:105].