# config/urls.py

from django.contrib import admin
from django.urls import include, path
from .views import DocsIndexView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

from app_materials.views import CourseSubscriptionToggleView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", DocsIndexView.as_view(), name="docs-index"),

    # Модули/приложения.
    path("app_materials/", include("app_materials.urls")),
    path("app_users/", include("app_users.urls")),

    # Токены доступа.
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # Подписка/отписка.
    path("course/<int:course_id>/subscribe/", CourseSubscriptionToggleView.as_view(), name="course-subscription"),

    # Документация моего API, первичный OpenAPI (JSON/YAML).
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    # В оболочке Swagger UI интерфейс.
    path("api/schema/swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    # В оболочке ReDoc интерфейс.
    path("api/schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

# Для справки:

# ViewSet
# GET /app_materials/courses/ — список курсов.
# POST /app_materials/courses/ — создание курса.
# GET /app_materials/courses/{id}/ — один курс.
# PUT /app_materials/courses/{id}/ — полное обновление.
# PATCH /app_materials/courses/{id}/ — частичное обновление.
# DELETE /app_materials/courses/{id}/ — удаление курса.

# Generics
# GET http://127.0.0.1:8000/app_materials/lessons/ — список уроков.
# POST http://127.0.0.1:8000/app_materials/lessons/create/ — создание урока.
# GET http://127.0.0.1:8000/app_materials/lessons/{id}/ — один урок.
# PUT http://127.0.0.1:8000/app_materials/lessons/{id}/update/ — обновление урока.
# DELETE http://127.0.0.1:8000/app_materials/lessons/{id}/delete/ — удаление урока.

# Docs
# /api/schema/ - OpenAPI-схема (JSON).
# /api/schema/swagger/ - Swagger UI.
# /api/schema/redoc/ - ReDoc.