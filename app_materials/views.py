# app_materials/views.py

from django.shortcuts import get_object_or_404
from rest_framework import generics, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app_users.permissions import IsModer, IsOwner

from .models import Course, Lesson, Subscription
from .paginators import CourseLessonPagination
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
    pagination_class = CourseLessonPagination

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
            permission_classes = [IsAuthenticated, IsOwner | IsModer]
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
    pagination_class = CourseLessonPagination


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


class CourseSubscriptionToggleView(APIView):
    """
    Эндпоинт для установки/снятия подписки на курс текущего пользователя.
    POST:
      - если подписка есть → удалить, message="подписка удалена"
      - если подписки нет → создать, message="подписка добавлена"
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, course_id, *args, **kwargs):
        user = request.user
        course_item = get_object_or_404(Course, pk=course_id)  # 404 error, если курса нет.

        subs_qs = Subscription.objects.filter(user=user, course=course_item)

        if subs_qs.exists():
            subs_qs.delete()
            message = "подписка удалена"
        else:
            Subscription.objects.create(user=user, course=course_item)
            message = "подписка добавлена"

        return Response({"message": message}, status=status.HTTP_200_OK)
