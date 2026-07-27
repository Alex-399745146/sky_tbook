# app_materials/tests.py

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Course, Lesson, Subscription

User = get_user_model()


class BaseAPITestCase(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(email="owner@example.com", password="pass123")
        self.moder = User.objects.create_user(email="moder@example.com", password="pass123", is_staff=True)
        self.user = User.objects.create_user(email="user@example.com", password="pass123")

        self.course = Course.objects.create(
            name="Тестовый курс",
            description="Описание",
            owner=self.owner,
        )

        self.lesson = Lesson.objects.create(
            course=self.course,
            name="Урок 1",
            description="Описание урока",
            video_url="https://youtube.com/watch?v=123",
            owner=self.owner,
        )


class TestLessonBasicCRUD(BaseAPITestCase):
    def test_list_lessons(self):
        self.client.force_authenticate(user=self.owner)
        url = reverse("app_materials:lesson-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data["count"], 1)
        names = [item["name"] for item in response.data["results"]]
        self.assertIn("Урок 1", names)

    def test_create_lesson(self):
        self.client.force_authenticate(user=self.owner)
        url = reverse("app_materials:lesson-create")
        data = {
            "course": self.course.id,
            "name": "Новый урок",
            "description": "Описание",
            "video_url": "https://youtube.com/watch?v=456",
        }
        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Новый урок")
        self.assertTrue(Lesson.objects.filter(name="Новый урок").exists())


class TestCourseSubscription(BaseAPITestCase):
    def test_subscribe_and_unsubscribe(self):
        self.client.force_authenticate(user=self.user)
        # теперь без namespace, берём имя из config.urls
        url = reverse("app_materials:course-subscription", kwargs={"course_id": self.course.id})

        # подписка
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "подписка добавлена")

        # отписка
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "подписка удалена")
