# sky_tbook

Учебный Django‑проект LMS (Learning Management System) для онлайн‑курсов с API на Django REST Framework.

## Описание

Проект реализует базовый функционал LMS:

- управление курсами и уроками;
- вложенный вывод уроков внутри курса (количество и список);
- работа с пользователями и их профилями;
- учёт платежей за курсы и отдельные уроки;
- авторизация по JWT‑токенам и разграничение прав доступа (модераторы, владельцы объектов).

## Технологии

- Python 3.13
- Django 4.2
- Django REST Framework 3.17
- djangorestframework‑simplejwt (JWT‑аутентификация)
- PostgreSQL
- Pillow (работа с изображениями)
- python‑dotenv

## Структура

Основные приложения:

- `app_materials` — курсы и уроки (`Course`, `Lesson`, сериализаторы с количеством и списком уроков, API).
- `app_users` — пользователи (кастомная модель `User` по email, профиль, модель `Payment` для оплат, права доступа и группы).

Главные файлы:

- `config/settings.py` — настройки проекта, включая `REST_FRAMEWORK` и JWT‑аутентификацию.
- `config/urls.py` — корневые маршруты и эндпоинты получения/обновления JWT‑токенов.
- `app_materials/models.py` — модели `Course` и `Lesson` с полем владельца (`owner`).
- `app_materials/serializers.py` — сериализаторы курсов и уроков (вложенные уроки и `lessons_count`).
- `app_materials/views.py` — ViewSet для `Course` и Generic‑вью для `Lesson` с разграничением прав по ролям и владельцам.
- `app_materials/urls.py` — маршруты API курсов и уроков.
- `app_users/models.py` — кастомный `User` и `Payment`.
- `app_users/serializers.py` — сериализаторы пользователя и платежей.
- `app_users/permissions.py` — кастомные пермишены `IsModer` и `IsOwner`.
- `app_users/urls.py` — маршруты API пользователей (CRUD, регистрация) и платежей.
- `users/fixtures/groups.json` — фикстура с группами (например, группа модераторов).

## Установка и запуск

```bash
# клонировать репозиторий
git clone https://github.com/Alex-399745146/sky_tbook.git
cd sky_tbook

# установить зависимости через Poetry
poetry install

# применить миграции
poetry run python manage.py migrate

# загрузить группы (например, модераторов)
poetry run python manage.py loaddata users/fixtures/groups.json

# создать суперпользователя
poetry run python manage.py createsuperuser

# запустить сервер разработки
poetry run python manage.py runserver
```

После запуска сервер будет доступен по адресу:

- `http://127.0.0.1:8000/`

## Аутентификация и авторизация

### JWT‑токены

Используется библиотека Simple JWT.

Эндпоинты:

- `POST /api/token/` — получить пару `access`/`refresh` токенов.
- `POST /api/token/refresh/` — обновить `access` токен по действующему `refresh`.

Эти эндпоинты доступны без авторизации (`AllowAny`).

Для доступа к защищённым API нужно:

- отправлять заголовок `Authorization: Bearer <access_token>`.

### Пользователи

Эндпоинты (префикс `/app_users/`):

- `POST /app_users/users/register/` — регистрация пользователя (доступен без авторизации).
- `GET /app_users/users/` — список пользователей (только для авторизованных).
- `GET /app_users/users/{id}/` — получить пользователя.
- `PUT/PATCH /app_users/users/{id}/` — обновить пользователя.
- `DELETE /app_users/users/{id}/` — удалить пользователя.

Все CRUD‑операции по пользователя (кроме регистрации и получения токенов) закрыты авторизацией (`IsAuthenticated`).

### Группы и роли

Используются стандартные группы Django:

- группа `moderators` — модераторы.

Кастомные пермишены:

- `IsModer` — проверяет, что пользователь состоит в группе `moderators`.  
- `IsOwner` — проверяет, что пользователь является владельцем конкретного объекта (`obj.owner == request.user`).

Группы назначаются пользователям через админ‑панель Django.

## API эндпоинты

### Курсы (Course)

Базовый префикс: `/app_materials/`

- `GET /app_materials/courses/` — список курсов (с количеством уроков и вложенными уроками).
- `POST /app_materials/courses/` — создание курса.
- `GET /app_materials/courses/{id}/` — получить курс.
- `PUT /app_materials/courses/{id}/` — обновить курс.
- `PATCH /app_materials/courses/{id}/` — частично обновить курс.
- `DELETE /app_materials/courses/{id}/` — удалить курс.

Права:

- модератор (`moderators`):
  - может просматривать и редактировать любые курсы;
  - не может создавать и удалять курсы.
- обычный авторизованный пользователь:
  - может просматривать, обновлять и удалять только **свои** курсы (по полю `owner`).

### Уроки (Lesson)

- `GET /app_materials/lessons/` — список уроков.
- `POST /app_materials/lessons/create/` — создание урока.
- `GET /app_materials/lessons/{id}/` — получить урок.
- `PUT /app_materials/lessons/{id}/update/` — обновить урок.
- `DELETE /app_materials/lessons/{id}/delete/` — удалить урок.

Права:

- модератор:
  - может просматривать и редактировать любые уроки;
  - не может создавать и удалять уроки.
- обычный пользователь:
  - может просматривать, редактировать и удалять только **свои** уроки (по `owner`).

### Платежи (Payment)

Базовый префикс: `/app_users/`

- `GET /app_users/payments/` — список платежей с фильтрацией и сортировкой:
  - `?ordering=asc|desc` — порядок по дате оплаты;
  - `?course={id}` — фильтр по курсу;
  - `?lesson={id}` — фильтр по уроку;
  - `?method=cash|transfer` — фильтр по способу оплаты.

Доступ к платежам ограничен авторизованным пользователям; дополнительные ограничения можно накладывать в контроллерах (например, выводить только свои платежи).

## Права доступа (объектный уровень)

Для проверки прав доступа используются:

- глобальные настройки `DEFAULT_AUTHENTICATION_CLASSES` (JWT) и `DEFAULT_PERMISSION_CLASSES` (`IsAuthenticated`) в `settings.py`.
- кастомные пермишены на уровне контроллеров (ViewSet и Generics) через:
  - метод `get_permissions()` для ViewSet (разные права для разных `action`);
  - `permission_classes` для GenericAPIView.

Примеры комбинаций:

- только авторизованные и не‑модераторы:
  - `permission_classes = [IsAuthenticated, ~IsModer]`
- авторизованные и либо модераторы, либо владельцы:
  - `permission_classes = [IsAuthenticated, IsModer | IsOwner]`

## Проверка через Postman

1. Запусти сервер: `poetry run python manage.py runserver`.
2. Получи JWT‑токены:
   - `POST /api/token/` с email/паролем.
3. В запросах к защищённым эндпоинтам используй заголовок:
   - `Authorization: Bearer <access_token>`.
4. Проверь:
   - регистрацию пользователя без токена;
   - запрет доступа к курсам/урокам без токена;
   - права модератора (нет создания/удаления, есть просмотр/редактирование);
   - права обычного пользователя (только свои курсы/уроки).

## Статус

Проект используется для выполнения домашних заданий по Django/DRF с акцентом на:

- JWT‑аутентификацию;
- разграничение прав доступа по ролям и владельцам;
- работу с вложенными ресурсами и платежами.