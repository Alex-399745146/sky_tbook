# app_materials/serializers.py

from rest_framework import serializers

from .models import Course, Lesson
from .validators import validate_video_url


class LessonSerializer(serializers.ModelSerializer):
    video_url = serializers.CharField(
        max_length=255,
        validators=[validate_video_url],  # Подключение к модулю с кастомным валидатором.
        help_text="Ссылка на видео с youtube.com",
    )

    class Meta:
        model = Lesson
        fields = (
            "name",
            "description",
            "preview",
            "video_url",
            "owner",
        )


class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = (
            "name",
            "preview",
            "description",
            # другие поля курса
            "lessons_count",
            "lessons",
            "owner",
        )

    def get_lessons_count(self, obj):
        # obj — это конкретный Course
        return obj.lessons.count()
