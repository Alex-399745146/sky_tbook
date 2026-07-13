# app_materials/views.py

from rest_framework import generics, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated

from app_users.permissions import IsModer, IsOwner

from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """
    ViewSet для модели Course.

    Предоставляет полный набор стандартных CRUD‑операций:
    list, retrieve, create, update, partial_update, destroy.
    Базируется на queryset всех курсов и CourseSerializer.
    """

    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        # По умолчанию только авторизованные.
        if self.action in ["list", "retrieve"]:
            # Просмотр: авторизованные или модератор, или владелец.
            permission_classes = [IsAuthenticated, IsModer | IsOwner]
        elif self.action in ["update", "partial_update"]:
            # Редактировать: модераторы (любые объекты) или владельцы.
            permission_classes = [IsAuthenticated, IsModer | IsOwner]
        elif self.action == "destroy":
            # Удалять: только владельцы, модераторы НЕ могут удалять.
            permission_classes = [IsAuthenticated, IsOwner & ~IsModer]
        elif self.action == "create":
            # Создание курса: авторизованные НЕ‑модераторы (модератор не может создавать).
            permission_classes = [IsAuthenticated, ~IsModer]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]


class LessonListAPIView(generics.ListAPIView):
    """
    Представление только для чтения списка уроков.

    Обрабатывает GET‑запросы и возвращает коллекцию объектов Lesson,
    сериализованных через LessonSerializer.
    """

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsModer | IsOwner]


class LessonCreateAPIView(generics.CreateAPIView):
    """
    Представление только для создания нового урока.

    Обрабатывает POST‑запросы, валидирует входные данные
    с помощью LessonSerializer и сохраняет новый объект Lesson.
    """

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, ~IsModer]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonRetrieveAPIView(generics.RetrieveAPIView):
    """
    Представление для получения одного урока по первичному ключу.

    Обрабатывает GET‑запросы к деталям ресурса Lesson и
    возвращает один объект, сериализованный LessonSerializer.
    """

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsModer | IsOwner]


class LessonUpdateAPIView(generics.UpdateAPIView):
    """
    Представление для обновления существующего урока.

    Поддерживает PUT/PATCH‑запросы, применяет LessonSerializer
    для валидации и сохранения изменений объекта Lesson.
    """

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class LessonDestroyAPIView(generics.DestroyAPIView):
    """
    Представление для удаления урока.

    Обрабатывает DELETE‑запросы и удаляет выбранный объект Lesson
    из queryset.
    """

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsOwner & ~IsModer]
