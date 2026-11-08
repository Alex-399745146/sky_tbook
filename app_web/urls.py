# app_web/urls.py

from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import (
    CourseDetailView,
    CourseListView,
    EmailLoginView,
    PaymentListView,
    ProfileView,
    RegisterView,
    SubscriptionToggleView,
)

app_name = "app_web"

urlpatterns = [
    path("", CourseListView.as_view(), name="home"),
    path("courses/<int:pk>/", CourseDetailView.as_view(), name="course-detail"),
    path("courses/<int:pk>/subscribe/", SubscriptionToggleView.as_view(), name="course-subscribe"),
    path("login/", EmailLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(next_page="app_web:home"), name="logout"),
    path("register/", RegisterView.as_view(), name="register"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("payments/", PaymentListView.as_view(), name="payments"),
]
