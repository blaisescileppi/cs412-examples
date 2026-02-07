## formdata/urls.py
## url patterns for the 'formdata' app

from django.urls import path
from django.conf import settings
from . import views

# URL patterns for this app
urlpatterns = [
    path(r'', views.show_form, name='show_form'), 
    path(r'submit', views.submit, name='submit'), ## NEW
]