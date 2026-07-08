# app_materials/serializers.py

from rest_framework import serializers

from .models import Course, Lesson


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = "__all__"


class CourseSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    lessons_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = (
            'name',
            'preview',
            'description',
            # добавленое динамическое поле
            'lessons_count',
        )

    def get_lessons_count(self, obj):
        # obj — это конкретный Course
        return obj.lessons.count()
