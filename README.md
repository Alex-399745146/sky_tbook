# sky_tbook

Учебный Django-проект для онлайн‑курсов с API на Django REST Framework.

## Описание

Проект реализует базовый функционал LMS:

- управление курсами;
- управление уроками внутри курса;
- (в дальнейшем) работа с пользователями и их профилями.

## Технологии

- Python 3.13
- Django 4.2
- Django REST Framework 3.17
- PostgreSQL
- Pillow (для работы с изображениями)
- python-dotenv

## Структура

Основные приложения:

- `app_materials` — курсы и уроки (Course, Lesson, API).
- `app_users` — пользователи (кастомная модель пользователя, профиль).

Главные файлы:

- `config/settings.py` — настройки проекта.
- `config/urls.py` — корневые маршруты.
- `app_materials/models.py` — модели Course и Lesson.
- `app_materials/serializers.py` — сериализаторы.
- `app_materials/views.py` — ViewSet для Course и Generic‑вью для Lesson.
- `app_materials/urls.py` — маршруты API курсов и уроков.

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

- `GET /app_materials/courses/` — список курсов.
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

## Проверка через Postman

Для проверки работы API:

1. Запусти сервер: `poetry run python manage.py runserver`.
2. В Postman создай коллекцию с запросами:
   - курсы: `GET/POST/PUT/PATCH/DELETE` на `/app_materials/courses/…`;
   - уроки: `GET/POST/PUT/DELETE` на `/app_materials/lessons/…`.
3. Используй `Content-Type: application/json` для `POST` и `PUT/PATCH`.

## Статус

Проект используется для выполнения домашних заданий по Django/DRF. В продакшн‑безопасность (аутентификация, права доступа) пока не реализована.