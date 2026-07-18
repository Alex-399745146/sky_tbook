# app_materials/models.py

from django.conf import settings
from django.db import models


class Course(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название")
    preview = models.ImageField(upload_to="course_previews/", verbose_name="Превью", null=True, blank=True)
    description = models.TextField(verbose_name="Описание", blank=True, null=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_courses",
        verbose_name="Владелец курса",
        null=True,  # временно, потом можно сделать обязательным
        blank=True,
    )

    def __str__(self):
        return self.name


class Lesson(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="lessons",
        verbose_name="Курс",
    )
    name = models.CharField(max_length=255, verbose_name="Название")
    description = models.TextField(verbose_name="Описание", blank=True, null=True)
    preview = models.ImageField(upload_to="lesson_previews/", verbose_name="Превью", null=True, blank=True)
    video_url = models.CharField(max_length=255, verbose_name="Ссылка на видео")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_lessons",
        verbose_name="Владелец урока",
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name


class Subscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="course_subscriptions",
        verbose_name="Пользователь",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name="Курс",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата подписки")

    class Meta:
        verbose_name = "Подписка на курс"
        verbose_name_plural = "Подписки на курс"

        constraints = [
            models.UniqueConstraint(
                fields=["user", "course"],
                name="unique_user_course_subscription",
            )
        ]

    def __str__(self):
        return f"Подписка {self.user} на {self.course}"
