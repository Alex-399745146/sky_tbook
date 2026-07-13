# app_users/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from app_users.views import UserViewSet, UserRegisterAPIView
from .views import PaymentListAPIView

app_name = "app_users"
router = DefaultRouter()
router.register('users', UserViewSet, basename='users')


urlpatterns = [
    path("payments/", PaymentListAPIView.as_view(), name="payments-list"),

    path('users/register/', UserRegisterAPIView.as_view(), name='users-register'),
    path('users/', include(router.urls)),
]
