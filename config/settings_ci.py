import os
from pathlib import Path

# Значения по умолчанию должны быть заданы до импорта settings.py:
# там есть проверка на небезопасный SECRET_KEY в production-режиме.
os.environ.setdefault("SECRET_KEY", "dev-secret-key-for-tests-only-32bytes")
os.environ.setdefault("DEBUG", "True")

from .settings import *  # noqa: E402,F403

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
DEBUG = True

# Для записи демо можно указать отдельный файл: SQLITE_DB=demo.sqlite3.
sqlite_db = os.getenv("SQLITE_DB")
sqlite_path = BASE_DIR / sqlite_db if sqlite_db else BASE_DIR / "test_db.sqlite3"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": sqlite_path,
    }
}

# Тесты не должны ходить во внешние сервисы и медленно хешировать пароли.
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_BROKER_URL = "memory://"
CELERY_RESULT_BACKEND = "cache+memory://"
