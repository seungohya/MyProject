# map/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path("api/crawl/", views.crawl, name="crawl"),
]
