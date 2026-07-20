from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from app_materials.views import CourseSubscriptionToggleView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("app_materials/", include("app_materials.urls")),
    path("app_users/", include("app_users.urls")),
    # Эндпоинты для access/refresh и их обновления.
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path(
        "course/<int:course_id>/subscribe/",
        CourseSubscriptionToggleView.as_view(),
        name="course-subscription",
    ),
]

# Для справки:

# ViewSet
# GET http://127.0.0.1:8000/app_materials/courses/ — список курсов.
# POST http://127.0.0.1:8000/app_materials/courses/ — создание курса.
# GET http://127.0.0.1:8000/app_materials/courses/{id}/ — один курс.
# PUT http://127.0.0.1:8000/app_materials/courses/{id}/ — полное обновление.
# PATCH http://127.0.0.1:8000/app_materials/courses/{id}/ — частичное обновление.
# DELETE http://127.0.0.1:8000/app_materials/courses/{id}/ — удаление курса.

# Generics
# GET http://127.0.0.1:8000/app_materials/lessons/ — список уроков.
# POST http://127.0.0.1:8000/app_materials/lessons/create/ — создание урока.
# GET http://127.0.0.1:8000/app_materials/lessons/{id}/ — один урок.
# PUT http://127.0.0.1:8000/app_materials/lessons/{id}/update/ — обновление урока.
# DELETE http://127.0.0.1:8000/app_materials/lessons/{id}/delete/ — удаление урока.
