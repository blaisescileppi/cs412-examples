# file: quotes/urls.py

from django.urls import path
from django.conf import settings
from . import views
 
 
urlpatterns = [ 
    path(r'', views.quote, name="quote"),
    path("quote/", views.quote, name="quote"),
    path("show_all/", views.show_all, name="show_all"),
    path("about/", views.about, name="about"),
]
