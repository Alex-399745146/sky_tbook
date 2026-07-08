# app_users/views.py

from rest_framework.generics import ListAPIView
from .models import Payment
from .serializers import PaymentSerializer


class PaymentListAPIView(ListAPIView):
    serializer_class = PaymentSerializer

    def get_queryset(self):
        qs = Payment.objects.all()

        # фильтр по курсу
        course_id = self.request.query_params.get('course')
        if course_id:
            qs = qs.filter(paid_course_id=course_id)

        # фильтр по уроку
        lesson_id = self.request.query_params.get('lesson')
        if lesson_id:
            qs = qs.filter(paid_lesson_id=lesson_id)

        # фильтр по способу оплаты
        method = self.request.query_params.get('method')
        if method:
            qs = qs.filter(payment_method=method)

        # сортировка по дате оплаты
        ordering = self.request.query_params.get('ordering')
        if ordering == 'asc':
            qs = qs.order_by('payment_date')
        elif ordering == 'desc':
            qs = qs.order_by('-payment_date')

        return qs