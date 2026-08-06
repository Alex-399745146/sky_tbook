# app_users/views.py

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Payment
from .serializers import CreatePaymentSerializer, PaymentSerializer, UserRegisterSerializer, UserSerializer
from .services import create_stripe_checkout_session, create_stripe_price, create_stripe_product

User = get_user_model()


class PaymentListAPIView(ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    # Какие фильтры включаем.
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    # Фильтрация по полям (курс, урок, способ оплаты).
    filterset_fields = ["paid_course", "paid_lesson", "payment_method"]

    # Поиск по email пользователя.
    search_fields = ["user__email"]

    # Сортировка по дате и сумме.
    ordering_fields = ["payment_date", "amount"]
    # Дефолт — новые сверху.
    ordering = ["-payment_date"]


class UserViewSet(viewsets.ModelViewSet):
    """
    Полный CRUD для пользователей.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    # Для Task 3 мы позже добавим IsOwner/ограничения по объектам.


class UserRegisterAPIView(generics.CreateAPIView):
    """
    Регистрация пользователя.
    """

    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]


class CreatePaymentView(generics.CreateAPIView):
    """
    Создаёт платеж в БД и возвращает ссылку на оплату в Stripe.
    POST /app_users/payments/create/
    Body:
    {
      "paid_course": 1,          # или paid_lesson
      "amount": "1000.00",       # в рублях
      "payment_method": "stripe"
    }
    """

    serializer_class = CreatePaymentSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        paid_course = serializer.validated_data.get("paid_course")
        paid_lesson = serializer.validated_data.get("paid_lesson")
        amount = serializer.validated_data["amount"]
        payment_method = serializer.validated_data.get("payment_method", "stripe")

        # Для простоты: название и описание берём из курса/урока.
        if paid_course:
            name = f"Курс: {paid_course.name}"
            description = paid_course.description or ""
        elif paid_lesson:
            name = f"Урок: {paid_lesson.name}"
            description = paid_lesson.description or ""
        else:
            return Response(
                {"detail": "Нужно указать paid_course или paid_lesson."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 1. Создаём платёж в БД.
        payment = Payment.objects.create(
            user=request.user,
            paid_course=paid_course,
            paid_lesson=paid_lesson,
            amount=amount,
            payment_method=payment_method,
        )

        # 2. Stripe: цена в копейках (или центах).
        amount_cents = int(amount * 100)

        # 3. Stripe: продукт -> цена -> сессия.
        product_id = create_stripe_product(paid_course, paid_lesson, name, description)
        price_id = create_stripe_price(product_id, amount_cents)
        session_url = create_stripe_checkout_session(price_id, request.user.email, payment.id)

        # 4. Сохраняем в платеж.
        payment.stripe_product_id = product_id
        payment.stripe_price_id = price_id
        payment.stripe_session_id = session_url  # в URL, но для простоты так
        payment.payment_url = session_url
        payment.save()

        # 5. Возвращаем информацию о платеже и ссылку.
        return Response(
            {
                "payment_id": payment.id,
                "amount": str(payment.amount),
                "payment_url": session_url,
            },
            status=status.HTTP_201_CREATED,
        )
