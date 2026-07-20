# app_materials/serializers.py

from rest_framework import serializers

from .models import Course, Lesson, Subscription
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
            "course",
            "name",
            "description",
            "preview",
            "video_url",
            "owner",
        )


class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)
    is_subscribed = serializers.SerializerMethodField()

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
            "is_subscribed",
        )

    def get_lessons_count(self, obj):
        # obj — это конкретный Course
        return obj.lessons.count()

    def get_is_subscribed(self, obj):
        """
        Возвращает True/False, подписан ли текущий пользователь на курс.
        """
        request = self.context.get("request")
        if request is None or request.user.is_anonymous:
            return False

        user = request.user
        return Subscription.objects.filter(user=user, course=obj).exists()
