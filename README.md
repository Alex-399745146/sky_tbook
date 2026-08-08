
## API Документация

После запуска проекта документация доступна по адресу:

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI схема**: http://localhost:8000/api/schema/

## Кратко по API

- **JWT**: POST `/api/token/`, POST `/api/token/refresh/`
- **Пользователи**: CRUD под `/app_users/users/`, регистрация `/register/`
- **Курсы**: `/app_materials/courses/` (CRUD, вложенные уроки)
- **Уроки**: `/app_materials/lessons/`
- **Подписки на курс**: эндпоинт toggle-подписки, рассылка писем при обновлении курса
- **Платежи**: `/app_users/payments/` с фильтрами по курсу/уроку и способу оплаты

## Управление задачами Celery

### Запуск воркера

```bash
docker compose exec web celery -A config worker --loglevel=info
```

### Запуск beat (периодические задачи)

```bash
docker compose exec web celery -A config beat --loglevel=info
```

### Периодическая задача (блокировка неактивных пользователей)

Задача `app_materials.tasks.deactivate_inactive_users_task` отключает пользователей, которые не заходили более месяца (`is_active = False` по полю `last_login`).

Расписание создаётся/обновляется командой:

```bash
python manage.py setup_deactivate_inactive_users_task
```

## Переменные окружения

### .env (локально, не коммитить!)

```env
DEBUG=True
SECRET_KEY=your-secret-key
DB_NAME=sky_tbook
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
REDIS_URL=redis://127.0.0.1:6379/0
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
```

### .env.docker (безопасные значения, можно коммитить)

```env
DEBUG=True
SECRET_KEY=django-insecure-dev-key
DB_NAME=sky_tbook
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
REDIS_URL=redis://redis:6379/0
STRIPE_PUBLISHABLE_KEY=pk_test_placeholder
STRIPE_SECRET_KEY=sk_test_placeholder
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
```

## Вклад в проект

1. Создай форк репозитория
2. Создай ветку `feature/your-feature`
3. Внеси изменения
4. Закоммить и запушь
5. Создай Pull Request

## Лицензия

MIT License

## Контакты

- **GitHub**: https://github.com/Alex-399745146/sky_tbook
- **Автор**: @Alex-399745146