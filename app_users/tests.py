# app_users/tests.py

from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from app_materials.models import Course, Lesson

from .models import Payment

User = get_user_model()


class BaseAPITestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.moderators, _ = Group.objects.get_or_create(name="moderators")

        cls.owner = User.objects.create_user(email="owner@example.com", password="StrongPass123!")
        cls.other = User.objects.create_user(email="other@example.com", password="StrongPass123!")
        cls.moderator = User.objects.create_user(email="moder@example.com", password="StrongPass123!")
        cls.moderator.groups.add(cls.moderators)

        cls.course = Course.objects.create(name="Тестовый курс", description="Описание", owner=cls.owner)
        cls.lesson = Lesson.objects.create(
            course=cls.course,
            name="Урок 1",
            description="Описание урока",
            video_url="https://youtube.com/watch?v=123",
            owner=cls.owner,
        )


class TestUserRegistration(BaseAPITestCase):
    def test_register_creates_user_with_hashed_password(self):
        url = reverse("app_users:users-register")
        data = {"email": "new@example.com", "password": "StrongPass123!", "city": "Москва"}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn("password", response.data)

        user = User.objects.get(email="new@example.com")
        self.assertTrue(user.check_password("StrongPass123!"))
        self.assertEqual(user.city, "Москва")

    def test_register_rejects_duplicate_email(self):
        url = reverse("app_users:users-register")
        data = {"email": self.owner.email, "password": "StrongPass123!"}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_register_rejects_weak_password(self):
        url = reverse("app_users:users-register")
        data = {"email": "weak@example.com", "password": "123"}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)


class TestJWT(BaseAPITestCase):
    def test_obtain_token_pair(self):
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"email": self.owner.email, "password": "StrongPass123!"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_access_token_opens_protected_endpoint(self):
        token_response = self.client.post(
            reverse("token_obtain_pair"),
            {"email": self.owner.email, "password": "StrongPass123!"},
            format="json",
        )
        access = token_response.data["access"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = self.client.get(reverse("app_materials:course-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_refresh_token_returns_new_access(self):
        token_response = self.client.post(
            reverse("token_obtain_pair"),
            {"email": self.owner.email, "password": "StrongPass123!"},
            format="json",
        )

        response = self.client.post(
            reverse("token_refresh"),
            {"refresh": token_response.data["refresh"]},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_wrong_password_is_rejected(self):
        response = self.client.post(
            reverse("token_obtain_pair"),
            {"email": self.owner.email, "password": "wrong-password"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestUsersAccess(BaseAPITestCase):
    def test_anonymous_cannot_list_users(self):
        response = self.client.get(reverse("app_users:users-list"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_regular_user_cannot_list_users(self):
        self.client.force_authenticate(user=self.other)

        response = self.client.get(reverse("app_users:users-list"))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_moderator_can_list_users(self):
        self.client.force_authenticate(user=self.moderator)

        response = self.client.get(reverse("app_users:users-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data["count"], 3)

    def test_user_can_retrieve_self(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.get(reverse("app_users:users-detail", kwargs={"pk": self.owner.pk}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.owner.email)

    def test_user_cannot_retrieve_another_user(self):
        self.client.force_authenticate(user=self.other)

        response = self.client.get(reverse("app_users:users-detail", kwargs={"pk": self.owner.pk}))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_moderator_can_retrieve_another_user(self):
        self.client.force_authenticate(user=self.moderator)

        response = self.client.get(reverse("app_users:users-detail", kwargs={"pk": self.owner.pk}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_update_self(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.patch(
            reverse("app_users:users-detail", kwargs={"pk": self.owner.pk}),
            {"city": "Санкт-Петербург"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.owner.refresh_from_db()
        self.assertEqual(self.owner.city, "Санкт-Петербург")

    def test_user_cannot_update_another_user(self):
        self.client.force_authenticate(user=self.other)

        response = self.client.patch(
            reverse("app_users:users-detail", kwargs={"pk": self.owner.pk}),
            {"city": "Казань"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_regular_user_cannot_delete_user(self):
        self.client.force_authenticate(user=self.other)

        response = self.client.delete(reverse("app_users:users-detail", kwargs={"pk": self.owner.pk}))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(User.objects.filter(pk=self.owner.pk).exists())

    def test_moderator_can_delete_user(self):
        victim = User.objects.create_user(email="victim@example.com", password="StrongPass123!")
        self.client.force_authenticate(user=self.moderator)

        response = self.client.delete(reverse("app_users:users-detail", kwargs={"pk": victim.pk}))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(pk=victim.pk).exists())


class TestPaymentAPI(BaseAPITestCase):
    def _create_payment(self, user, amount="1000.00", method=Payment.STRIPE, course=None, lesson=None):
        return Payment.objects.create(
            user=user,
            paid_course=course if course is not None else self.course,
            paid_lesson=lesson,
            amount=amount,
            payment_method=method,
        )

    @patch("app_users.views.create_stripe_checkout_session")
    @patch("app_users.views.create_stripe_price")
    @patch("app_users.views.create_stripe_product")
    def test_create_payment_stores_stripe_data(self, product_mock, price_mock, session_mock):
        product_mock.return_value = "prod_test"
        price_mock.return_value = "price_test"
        session_mock.return_value = SimpleNamespace(id="cs_test", url="https://checkout.stripe.com/c/cs_test")
        self.client.force_authenticate(user=self.other)

        response = self.client.post(
            reverse("app_users:payment-create"),
            {"paid_course": self.course.id, "amount": "1000.00", "payment_method": Payment.STRIPE},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["payment_url"], "https://checkout.stripe.com/c/cs_test")

        payment = Payment.objects.get(pk=response.data["payment_id"])
        self.assertEqual(payment.user, self.other)
        self.assertEqual(payment.stripe_product_id, "prod_test")
        self.assertEqual(payment.stripe_price_id, "price_test")
        self.assertEqual(payment.stripe_session_id, "cs_test")
        self.assertEqual(payment.payment_url, "https://checkout.stripe.com/c/cs_test")
        price_mock.assert_called_once_with("prod_test", 100000)

    @patch("app_users.views.create_stripe_checkout_session")
    @patch("app_users.views.create_stripe_price")
    @patch("app_users.views.create_stripe_product")
    def test_create_payment_for_lesson(self, product_mock, price_mock, session_mock):
        product_mock.return_value = "prod_test"
        price_mock.return_value = "price_test"
        session_mock.return_value = SimpleNamespace(id="cs_test", url="https://checkout.stripe.com/c/cs_test")
        self.client.force_authenticate(user=self.other)

        response = self.client.post(
            reverse("app_users:payment-create"),
            {"paid_lesson": self.lesson.id, "amount": "500.00", "payment_method": Payment.CASH},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        payment = Payment.objects.get(pk=response.data["payment_id"])
        self.assertEqual(payment.paid_lesson, self.lesson)
        self.assertIsNone(payment.paid_course)

    def test_create_payment_requires_exactly_one_target(self):
        self.client.force_authenticate(user=self.other)
        url = reverse("app_users:payment-create")

        no_target = self.client.post(url, {"amount": "100.00", "payment_method": Payment.CASH}, format="json")
        both_targets = self.client.post(
            url,
            {
                "paid_course": self.course.id,
                "paid_lesson": self.lesson.id,
                "amount": "100.00",
                "payment_method": Payment.CASH,
            },
            format="json",
        )

        self.assertEqual(no_target.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(both_targets.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_payment_rejects_non_positive_amount(self):
        self.client.force_authenticate(user=self.other)

        response = self.client.post(
            reverse("app_users:payment-create"),
            {"paid_course": self.course.id, "amount": "0.00", "payment_method": Payment.CASH},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_anonymous_cannot_create_payment(self):
        response = self.client.post(
            reverse("app_users:payment-create"),
            {"paid_course": self.course.id, "amount": "100.00", "payment_method": Payment.CASH},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_sees_only_own_payments(self):
        own_payment = self._create_payment(self.other)
        self._create_payment(self.owner, method=Payment.CASH)
        self.client.force_authenticate(user=self.other)

        response = self.client.get(reverse("app_users:payments-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["id"], own_payment.id)

    def test_moderator_sees_all_payments(self):
        self._create_payment(self.other)
        self._create_payment(self.owner, method=Payment.CASH)
        self.client.force_authenticate(user=self.moderator)

        response = self.client.get(reverse("app_users:payments-list"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_payments_can_be_filtered_by_method(self):
        self._create_payment(self.other, method=Payment.STRIPE)
        self._create_payment(self.other, method=Payment.CASH)
        self.client.force_authenticate(user=self.other)

        response = self.client.get(reverse("app_users:payments-list"), {"payment_method": Payment.CASH})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["payment_method"], Payment.CASH)

    def test_anonymous_cannot_list_payments(self):
        response = self.client.get(reverse("app_users:payments-list"))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TestUserModel(BaseAPITestCase):
    def test_create_user_requires_email(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", password="StrongPass123!")

    def test_create_superuser_sets_flags(self):
        admin = User.objects.create_superuser(email="admin@example.com", password="StrongPass123!")

        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)

    def test_user_str_is_email(self):
        self.assertEqual(str(self.owner), self.owner.email)

    def test_payment_str_contains_user_and_amount(self):
        payment = Payment.objects.create(
            user=self.owner,
            paid_course=self.course,
            amount="1000.00",
            payment_method=Payment.STRIPE,
        )

        self.assertIn(self.owner.email, str(payment))
        self.assertIn("1000.00", str(payment))
