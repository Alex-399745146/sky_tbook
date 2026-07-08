# app_users/urls.py

from django.urls import path

from . import views

app_name = "app_users"

urlpatterns = [
    # временная заглушка, чтобы всё работало
    path("", views.index, name="index"),
]
