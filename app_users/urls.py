# app_users/urls.py

from django.urls import path

from .views import PaymentListAPIView

app_name = "app_users"

urlpatterns = [
    path("payments/", PaymentListAPIView.as_view(), name="payments-list"),
]
