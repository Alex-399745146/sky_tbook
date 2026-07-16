# app_users/admin.py

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

User = get_user_model()


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Админ-класс для кастомной модели User.
    Наследуемся от стандартного UserAdmin, чтобы:
    - использовать готовые формы создания/редактирования;
    - сохранить привычный интерфейс админки.
    """

    # Поля, которые показываем в списке пользователей
    list_display = ("id", "email", "phone", "city", "is_staff", "is_active")
    search_fields = ("id", "email", "phone", "city")

    # Указываем, что поле логина — email
    ordering = ("email",)

    # Если ты убрал username, можно подправить fieldsets, чтобы его не было:
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Персональные данные", {"fields": ("avatar", "phone", "city")}),
        ("Права", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Важные даты", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "is_staff", "is_active"),
            },
        ),
    )
