# file: hw/urls.py

from django.urls import path
from django.conf import settings
from . import views

# URL patterns specific to hw app
urlpatterns = [
    path(r'', views.home_page, name = "home_page"),
    path(r'about', views.about, name = "about_page"),
]