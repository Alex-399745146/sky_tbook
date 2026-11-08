# app_users/views.py

from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from app_materials.paginators import CourseLessonPagination

from .models import Payment
from .permissions import IsModer, IsSelfOrModerator, is_moderator
from .serializers import CreatePaymentSerializer, PaymentSerializer, UserRegisterSerializer, UserSerializer
from .services import create_stripe_checkout_session, create_stripe_price, create_stripe_product

User = get_user_model()


class PaymentListAPIView(ListAPIView):
    """История платежей: пользователь видит только свои, модератор — все."""

    queryset = Payment.objects.none()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CourseLessonPagination

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

    def get_queryset(self):
        # При генерации OpenAPI-схемы пользователя ещё нет.
        if getattr(self, "swagger_fake_view", False) or not self.request.user.is_authenticated:
            return Payment.objects.none()

        queryset = Payment.objects.select_related("user", "paid_course", "paid_lesson")
        if is_moderator(self.request.user):
            return queryset
        return queryset.filter(user=self.request.user)


class UserViewSet(viewsets.ModelViewSet):
    """CRUD пользователей.

    Список и удаление доступны модераторам, работу со своим профилем —
    владельцу профиля, с чужим — модератору.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = CourseLessonPagination

    def get_permissions(self):
        if self.action in ["list", "create", "destroy"]:
            permission_classes = [IsAuthenticated, IsModer]
        elif self.action in ["retrieve", "update", "partial_update"]:
            permission_classes = [IsAuthenticated, IsSelfOrModerator]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]


class UserRegisterAPIView(generics.CreateAPIView):
    """Регистрация пользователя."""

    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]


class CreatePaymentView(generics.CreateAPIView):
    """Создаёт платёж в БД и возвращает ссылку на оплату в Stripe.

    POST /app_users/payments/create/
    Body:
    {
      "paid_course": 1,          # или paid_lesson
      "amount": "1000.00",       # в рублях
      "payment_method": "stripe"
    }
    """

    serializer_class = CreatePaymentSerializer
    permission_classes = [IsAuthenticated]

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
        else:
            name = f"Урок: {paid_lesson.name}"
            description = paid_lesson.description or ""

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
        session = create_stripe_checkout_session(price_id, request.user.email, payment.id)

        # 4. Сохраняем в платёж.
        payment.stripe_product_id = product_id
        payment.stripe_price_id = price_id
        payment.stripe_session_id = session.id
        payment.payment_url = session.url
        payment.save()

        # 5. Возвращаем информацию о платеже и ссылку.
        return Response(
            {
                "payment_id": payment.id,
                "amount": str(payment.amount),
                "payment_url": session.url,
            },
            status=status.HTTP_201_CREATED,
        )
