# app_web/urls.py

from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import (
    CourseCreateView,
    CourseDeleteView,
    CourseDetailView,
    CourseListView,
    CourseUpdateView,
    EmailLoginView,
    LessonCreateView,
    LessonDeleteView,
    LessonUpdateView,
    PaymentListView,
    ProfileView,
    RegisterView,
    SubscriptionToggleView,
)

app_name = "app_web"

urlpatterns = [
    path("", CourseListView.as_view(), name="home"),
    path("courses/new/", CourseCreateView.as_view(), name="course-create"),
    path("courses/<int:pk>/", CourseDetailView.as_view(), name="course-detail"),
    path("courses/<int:pk>/edit/", CourseUpdateView.as_view(), name="course-edit"),
    path("courses/<int:pk>/delete/", CourseDeleteView.as_view(), name="course-delete"),
    path("courses/<int:pk>/subscribe/", SubscriptionToggleView.as_view(), name="course-subscribe"),
    path("lessons/new/", LessonCreateView.as_view(), name="lesson-create"),
    path("lessons/<int:pk>/edit/", LessonUpdateView.as_view(), name="lesson-edit"),
    path("lessons/<int:pk>/delete/", LessonDeleteView.as_view(), name="lesson-delete"),
    path("login/", EmailLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(next_page="app_web:home"), name="logout"),
    path("register/", RegisterView.as_view(), name="register"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("payments/", PaymentListView.as_view(), name="payments"),
]
