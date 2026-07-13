# app_users/views.py

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView

from .models import Payment
from .serializers import PaymentSerializer


class PaymentListAPIView(ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    # Какие фильтры включаем.
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]

    # Фильтрация по полям (курс, урок, способ оплаты).
    filterset_fields = ['paid_course', 'paid_lesson', 'payment_method']

    # Поиск по email пользователя.
    search_fields = ['user__email']

    # Сортировка по дате и сумме.
    ordering_fields = ['payment_date', 'amount']
    # Дефолт — новые сверху.
    ordering = ['-payment_date']
