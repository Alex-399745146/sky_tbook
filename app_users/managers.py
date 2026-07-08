# app_users/managers.py

"""Кастомные менеджеры моделей."""

from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    """
    Кастомный менеджер пользователей.

    Нужен, чтобы:
    - создавать пользователей по email (а не по username);
    - корректно работать с createsuperuser.
    """

    def _create_user(self, email, password, **extra_fields):
        """Базовый метод создания пользователя."""
        if not email:
            raise ValueError("У пользователя должен быть указан email")
        # Приводим email к нормальному виду (lowercase, убираем пробелы и т.п.)
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # хешируем пароль
        user.save(using=self._db)  # сохраняем в БД, учитывая правильный alias
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Создание обычного пользователя (без прав админа)."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        """Создание суперпользователя (админа)."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(email, password, **extra_fields)
