from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("app_materials/", include("app_materials.urls")),
    path("app_users/", include("app_users.urls")),
]

# Для справки:

# ViewSet
# GET http://127.0.0.1:8000/app_materials/courses/ — список курсов.
#
# POST http://127.0.0.1:8000/app_materials/courses/ — создание курса.
#
# GET http://127.0.0.1:8000/app_materials/courses/{id}/ — один курс.
#
# PUT http://127.0.0.1:8000/app_materials/courses/{id}/ — полное обновление.
#
# PATCH http://127.0.0.1:8000/app_materials/courses/{id}/ — частичное обновление.
#
# DELETE http://127.0.0.1:8000/app_materials/courses/{id}/ — удаление курса.
#
# Generics
# GET http://127.0.0.1:8000/app_materials/lessons/ — список уроков.
#
# POST http://127.0.0.1:8000/app_materials/lessons/create/ — создание урока.
#
# GET http://127.0.0.1:8000/app_materials/lessons/{id}/ — один урок.
#
# PUT http://127.0.0.1:8000/app_materials/lessons/{id}/update/ — обновление урока.
#
# DELETE http://127.0.0.1:8000/app_materials/lessons/{id}/delete/ — удаление урока.
