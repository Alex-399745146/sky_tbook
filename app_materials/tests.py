# app_materials/tests.py

from io import StringIO

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core import mail
from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Course, Lesson, Subscription

User = get_user_model()


class BaseAPITestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.moderators, _ = Group.objects.get_or_create(name="moderators")

        cls.owner = User.objects.create_user(email="owner@example.com", password="StrongPass123!")
        cls.other = User.objects.create_user(email="other@example.com", password="StrongPass123!")
        cls.moderator = User.objects.create_user(email="moder@example.com", password="StrongPass123!")
        cls.moderator.groups.add(cls.moderators)

        cls.course = Course.objects.create(
            name="Тестовый курс",
            description="Описание",
            owner=cls.owner,
        )
        cls.lesson = Lesson.objects.create(
            course=cls.course,
            name="Урок 1",
            description="Описание урока",
            video_url="https://youtube.com/watch?v=123",
            owner=cls.owner,
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

    def test_list_lessons_requires_authentication(self):
        response = self.client.get(reverse("app_materials:lesson-list"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_lesson_sets_owner(self):
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
        lesson = Lesson.objects.get(name="Новый урок")
        self.assertEqual(lesson.owner, self.owner)

    def test_moderator_cannot_create_lesson(self):
        self.client.force_authenticate(user=self.moderator)

        response = self.client.post(
            reverse("app_materials:lesson-create"),
            {
                "course": self.course.id,
                "name": "Урок модератора",
                "video_url": "https://youtube.com/watch?v=789",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_lesson_rejects_foreign_video_host(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.post(
            reverse("app_materials:lesson-create"),
            {
                "course": self.course.id,
                "name": "Плохой урок",
                "video_url": "https://vimeo.com/123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("video_url", response.data)

    def test_owner_can_update_lesson(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.patch(
            reverse("app_materials:lesson-update", kwargs={"pk": self.lesson.pk}),
            {"name": "Обновлённый урок"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.name, "Обновлённый урок")

    def test_stranger_cannot_update_lesson(self):
        self.client.force_authenticate(user=self.other)

        response = self.client.patch(
            reverse("app_materials:lesson-update", kwargs={"pk": self.lesson.pk}),
            {"name": "Чужое изменение"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_moderator_can_update_lesson(self):
        self.client.force_authenticate(user=self.moderator)

        response = self.client.patch(
            reverse("app_materials:lesson-update", kwargs={"pk": self.lesson.pk}),
            {"name": "Правка модератора"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_owner_can_delete_lesson(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.delete(reverse("app_materials:lesson-delete", kwargs={"pk": self.lesson.pk}))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Lesson.objects.filter(pk=self.lesson.pk).exists())

    def test_stranger_cannot_delete_lesson(self):
        self.client.force_authenticate(user=self.other)

        response = self.client.delete(reverse("app_materials:lesson-delete", kwargs={"pk": self.lesson.pk}))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Lesson.objects.filter(pk=self.lesson.pk).exists())

    def test_moderator_cannot_delete_lesson(self):
        self.client.force_authenticate(user=self.moderator)

        response = self.client.delete(reverse("app_materials:lesson-delete", kwargs={"pk": self.lesson.pk}))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestCourseAccess(BaseAPITestCase):
    def test_list_courses_requires_authentication(self):
        response = self.client.get(reverse("app_materials:course-list"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_owner_can_create_course(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.post(
            reverse("app_materials:course-list"),
            {"name": "Новый курс", "description": "Описание"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        course = Course.objects.get(name="Новый курс")
        self.assertEqual(course.owner, self.owner)

    def test_moderator_cannot_create_course(self):
        self.client.force_authenticate(user=self.moderator)

        response = self.client.post(
            reverse("app_materials:course-list"),
            {"name": "Курс модератора"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_update_course(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.patch(
            reverse("app_materials:course-detail", kwargs={"pk": self.course.pk}),
            {"name": "Обновлённый курс"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.course.refresh_from_db()
        self.assertEqual(self.course.name, "Обновлённый курс")

    def test_stranger_cannot_update_course(self):
        self.client.force_authenticate(user=self.other)

        response = self.client.patch(
            reverse("app_materials:course-detail", kwargs={"pk": self.course.pk}),
            {"name": "Чужое изменение"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_moderator_can_update_course(self):
        self.client.force_authenticate(user=self.moderator)

        response = self.client.patch(
            reverse("app_materials:course-detail", kwargs={"pk": self.course.pk}),
            {"name": "Правка модератора"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_owner_can_delete_course(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.delete(reverse("app_materials:course-detail", kwargs={"pk": self.course.pk}))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Course.objects.filter(pk=self.course.pk).exists())

    def test_stranger_cannot_delete_course(self):
        self.client.force_authenticate(user=self.other)

        response = self.client.delete(reverse("app_materials:course-detail", kwargs={"pk": self.course.pk}))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_moderator_cannot_delete_course(self):
        self.client.force_authenticate(user=self.moderator)

        response = self.client.delete(reverse("app_materials:course-detail", kwargs={"pk": self.course.pk}))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class TestCourseSubscription(BaseAPITestCase):
    def setUp(self):
        self.url = reverse("app_materials:course-subscription", kwargs={"course_id": self.course.id})

    def test_subscribe_and_unsubscribe(self):
        self.client.force_authenticate(user=self.other)

        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "подписка добавлена")
        self.assertTrue(Subscription.objects.filter(user=self.other, course=self.course).exists())

        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "подписка удалена")
        self.assertFalse(Subscription.objects.filter(user=self.other, course=self.course).exists())

    def test_subscription_is_unique_per_user_and_course(self):
        Subscription.objects.create(user=self.other, course=self.course)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Subscription.objects.create(user=self.other, course=self.course)

    def test_subscription_requires_authentication(self):
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_subscription_for_missing_course_returns_404(self):
        self.client.force_authenticate(user=self.other)
        url = reverse("app_materials:course-subscription", kwargs={"course_id": 999999})

        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_course_serializer_reports_subscription_state(self):
        self.client.force_authenticate(user=self.other)
        detail_url = reverse("app_materials:course-detail", kwargs={"pk": self.course.pk})

        before = self.client.get(detail_url)
        self.assertFalse(before.data["is_subscribed"])

        self.client.post(self.url)
        after = self.client.get(detail_url)
        self.assertTrue(after.data["is_subscribed"])


class TestCourseUpdateNotifications(BaseAPITestCase):
    def test_update_sends_email_to_subscribers(self):
        Subscription.objects.create(user=self.other, course=self.course)
        self.client.force_authenticate(user=self.owner)

        response = self.client.patch(
            reverse("app_materials:course-detail", kwargs={"pk": self.course.pk}),
            {"description": "Новое описание"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(self.course.name, mail.outbox[0].subject)
        self.assertEqual(mail.outbox[0].to, [self.other.email])

    def test_update_without_subscribers_sends_nothing(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.patch(
            reverse("app_materials:course-detail", kwargs={"pk": self.course.pk}),
            {"description": "Новое описание"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 0)


class TestModels(BaseAPITestCase):
    def test_course_str(self):
        self.assertEqual(str(self.course), self.course.name)

    def test_lesson_str(self):
        self.assertEqual(str(self.lesson), self.lesson.name)

    def test_subscription_str(self):
        subscription = Subscription.objects.create(user=self.other, course=self.course)

        self.assertIn(self.other.email, str(subscription))
        self.assertIn(self.course.name, str(subscription))


class TestSeedDemoCommand(TestCase):
    def test_seed_demo_creates_data_and_is_idempotent(self):
        call_command("seed_demo", stdout=StringIO())
        call_command("seed_demo", stdout=StringIO())

        emails = [
            "student@example.com",
            "teacher@example.com",
            "moderator@example.com",
            "admin@example.com",
        ]
        self.assertEqual(User.objects.filter(email__in=emails).count(), 4)
        self.assertEqual(Course.objects.filter(name="Python с нуля").count(), 1)
        self.assertEqual(Lesson.objects.filter(course__name="Python с нуля").count(), 3)

        student = User.objects.get(email="student@example.com")
        self.assertTrue(student.check_password("DemoPass123!"))
        self.assertEqual(student.payments.count(), 2)
        self.assertEqual(student.course_subscriptions.count(), 2)

        admin = User.objects.get(email="admin@example.com")
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_staff)
