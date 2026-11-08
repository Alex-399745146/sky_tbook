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

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "test_db.sqlite3",
    }
}

# Тесты не должны ходить во внешние сервисы и медленно хешировать пароли.
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_BROKER_URL = "memory://"
CELERY_RESULT_BACKEND = "cache+memory://"
