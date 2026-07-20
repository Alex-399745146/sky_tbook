# app_materials/paginators.py

from rest_framework.pagination import PageNumberPagination


class CourseLessonPagination(PageNumberPagination):
    # сколько объектов по умолчанию на одной странице
    page_size = 5

    # имя параметра запроса, через который клиент может выбрать страницу
    # GET /app_materials/courses/?page=2
    page_query_param = "page"

    # имя параметра запроса, через который можно переопределить page_size
    # GET /app_materials/courses/?page=1&page_size=10
    page_size_query_param = "page_size"

    # максимальный page_size, который допустимо задать через запрос
    max_page_size = 20
