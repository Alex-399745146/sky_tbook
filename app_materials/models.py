# app_materials/models.py

from django.db import models


class Course(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название")
    preview = models.ImageField(upload_to="course_previews/", verbose_name="Превью", null=True, blank=True)
    description = models.TextField(verbose_name="Описание", blank=True, null=True)

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

    def __str__(self):
        return self.name
