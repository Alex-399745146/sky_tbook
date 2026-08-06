# config/views.py

from django.views.generic import TemplateView


class DocsIndexView(TemplateView):
    template_name = "docs.html"
