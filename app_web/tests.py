# app_web/tests.py

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from app_materials.models import Course, Lesson, Subscription
from app_users.models import Payment

User = get_user_model()


class BaseWebTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.moderators, _ = Group.objects.get_or_create(name="moderators")

        cls.owner = User.objects.create_user(email="owner@example.com", password="StrongPass123!")
        cls.other = User.objects.create_user(email="other@example.com", password="StrongPass123!")
        cls.moderator = User.objects.create_user(email="moder@example.com", password="StrongPass123!")
        cls.moderator.groups.add(cls.moderators)

        cls.course = Course.objects.create(
            name="Django REST Framework",
            description="Практический курс по DRF: сериализаторы, ViewSet и права доступа.",
            owner=cls.owner,
        )
        cls.lesson = Lesson.objects.create(
            course=cls.course,
            name="Введение в DRF",
            description="Первый урок курса.",
            video_url="https://youtube.com/watch?v=123",
            owner=cls.owner,
        )


class TestCoursePages(BaseWebTestCase):
    def test_home_page_is_public(self):
        response = self.client.get(reverse("app_web:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.course.name)
        self.assertContains(response, "Каталог курсов")

    def test_search_filters_courses(self):
        Course.objects.create(name="SQL и PostgreSQL", description="Базы данных", owner=self.owner)

        response = self.client.get(reverse("app_web:home"), {"q": "Django"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Django REST Framework")
        self.assertNotContains(response, "SQL и PostgreSQL")

    def test_search_without_results_shows_message(self):
        response = self.client.get(reverse("app_web:home"), {"q": "несуществующий-курс"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Курсы не найдены")

    def test_course_detail_shows_lessons(self):
        response = self.client.get(reverse("app_web:course-detail", kwargs={"pk": self.course.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.course.name)
        self.assertContains(response, self.lesson.name)
        self.assertContains(response, "По подписке")

    def test_course_detail_404_for_missing_course(self):
        response = self.client.get(reverse("app_web:course-detail", kwargs={"pk": 999999}))

        self.assertEqual(response.status_code, 404)


class TestAuthentication(BaseWebTestCase):
    def test_login_page_renders(self):
        response = self.client.get(reverse("app_web:login"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Вход в аккаунт")

    def test_login_with_valid_credentials(self):
        response = self.client.post(
            reverse("app_web:login"),
            {"username": self.owner.email, "password": "StrongPass123!"},
        )

        self.assertRedirects(response, reverse("app_web:home"))
        self.assertEqual(int(self.client.session["_auth_user_id"]), self.owner.pk)

    def test_login_with_wrong_password_shows_error(self):
        response = self.client.post(
            reverse("app_web:login"),
            {"username": self.owner.email, "password": "wrong-password"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "правильные")

    def test_registration_creates_user_and_logs_in(self):
        response = self.client.post(
            reverse("app_web:register"),
            {
                "email": "new@example.com",
                "phone": "+79990000000",
                "city": "Москва",
                "password1": "StrongPass123!",
                "password2": "StrongPass123!",
            },
        )

        self.assertRedirects(response, reverse("app_web:home"))
        user = User.objects.get(email="new@example.com")
        self.assertTrue(user.check_password("StrongPass123!"))
        self.assertEqual(int(self.client.session["_auth_user_id"]), user.pk)

    def test_registration_rejects_password_mismatch(self):
        response = self.client.post(
            reverse("app_web:register"),
            {
                "email": "new@example.com",
                "password1": "StrongPass123!",
                "password2": "AnotherPass123!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Пароли не совпадают")
        self.assertFalse(User.objects.filter(email="new@example.com").exists())

    def test_registration_rejects_weak_password(self):
        response = self.client.post(
            reverse("app_web:register"),
            {"email": "new@example.com", "password1": "123", "password2": "123"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email="new@example.com").exists())

    def test_logout_requires_post_and_logs_out(self):
        self.client.force_login(self.owner)

        response = self.client.post(reverse("app_web:logout"))

        self.assertRedirects(response, reverse("app_web:home"))
        self.assertNotIn("_auth_user_id", self.client.session)


class TestProfile(BaseWebTestCase):
    def test_profile_requires_login(self):
        response = self.client.get(reverse("app_web:profile"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("app_web:login"), response.url)

    def test_profile_shows_current_user(self):
        self.client.force_login(self.owner)

        response = self.client.get(reverse("app_web:profile"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.owner.email)

    def test_profile_can_be_updated(self):
        self.client.force_login(self.owner)

        response = self.client.post(
            reverse("app_web:profile"),
            {"email": self.owner.email, "phone": "+79991112233", "city": "Санкт-Петербург"},
        )

        self.assertRedirects(response, reverse("app_web:profile"))
        self.owner.refresh_from_db()
        self.assertEqual(self.owner.city, "Санкт-Петербург")


class TestSubscription(BaseWebTestCase):
    def test_subscription_requires_login(self):
        response = self.client.post(reverse("app_web:course-subscribe", kwargs={"pk": self.course.pk}))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("app_web:login"), response.url)

    def test_subscribe_and_unsubscribe(self):
        self.client.force_login(self.other)
        url = reverse("app_web:course-subscribe", kwargs={"pk": self.course.pk})

        first = self.client.post(url)
        self.assertRedirects(first, reverse("app_web:course-detail", kwargs={"pk": self.course.pk}))
        self.assertTrue(Subscription.objects.filter(user=self.other, course=self.course).exists())

        second = self.client.post(url)
        self.assertRedirects(second, reverse("app_web:course-detail", kwargs={"pk": self.course.pk}))
        self.assertFalse(Subscription.objects.filter(user=self.other, course=self.course).exists())

    def test_subscriber_sees_video_links(self):
        Subscription.objects.create(user=self.other, course=self.course)
        self.client.force_login(self.other)

        response = self.client.get(reverse("app_web:course-detail", kwargs={"pk": self.course.pk}))

        self.assertContains(response, "Смотреть")
        self.assertNotContains(response, "По подписке")

    def test_owner_sees_video_links_without_subscription(self):
        self.client.force_login(self.owner)

        response = self.client.get(reverse("app_web:course-detail", kwargs={"pk": self.course.pk}))

        self.assertContains(response, "Смотреть")
        self.assertContains(response, "Управление доступно")


class TestPaymentsPage(BaseWebTestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.own_payment = Payment.objects.create(
            user=cls.other,
            paid_course=cls.course,
            amount="1000.00",
            payment_method=Payment.STRIPE,
        )
        cls.owner_payment = Payment.objects.create(
            user=cls.owner,
            paid_course=cls.course,
            amount="500.00",
            payment_method=Payment.CASH,
        )

    def test_payments_require_login(self):
        response = self.client.get(reverse("app_web:payments"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("app_web:login"), response.url)

    def test_user_sees_only_own_payments(self):
        self.client.force_login(self.other)

        response = self.client.get(reverse("app_web:payments"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Мои платежи")
        self.assertContains(response, "1000,00")
        self.assertNotContains(response, "500,00")

    def test_moderator_sees_all_payments(self):
        self.client.force_login(self.moderator)

        response = self.client.get(reverse("app_web:payments"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Все платежи")
        self.assertContains(response, "1000,00")
        self.assertContains(response, "500,00")
        self.assertContains(response, "1500,00")


class TestDocsPage(BaseWebTestCase):
    def test_docs_page_links_to_api(self):
        response = self.client.get(reverse("docs-index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Swagger UI")
        self.assertContains(response, "/api/schema/redoc/")
