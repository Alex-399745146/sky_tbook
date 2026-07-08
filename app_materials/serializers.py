# app_materials/serializers.py

from rest_framework import serializers

from .models import Course, Lesson


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ("name", "description", "preview", "video_url")


class CourseSerializer(serializers.ModelSerializer):
    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = (
            'name',
            'preview',
            'description',
            # другие поля курса
            'lessons_count',
            'lessons',
        )

    def get_lessons_count(self, obj):
        # obj — это конкретный Course
        return obj.lessons.count()
