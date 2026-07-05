# app_users/views.py

from django.http import HttpResponse


def index(request):
    return HttpResponse("app_users index page")
