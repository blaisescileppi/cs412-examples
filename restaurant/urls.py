## restaurant/urls.py
## url patterns for the 'restaurant' app

from django.urls import path
from django.conf import settings
from . import views

# URL patterns for this app
urlpatterns = [
    path(r'', views.main, name="main"), 
    path("main/", views.main, name="main"),
    path("orders/", views.orders, name='orders'),
    path("confirmation/", views.confirmation, name="confirmation"),
]
