# app_users/views.py

from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import Payment
from .serializers import PaymentSerializer, UserRegisterSerializer, UserSerializer

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
