# File: mini_insta/urls.py
# Author: Blaise Scileppi (blaises@bu.edu), February 10 2026
# Description: Defines URL patterns for the mini_insta application.
# Routes requests to views for displaying all profiles and individual profile detail pages.

from django.urls import path
from .views import ProfileListView, ProfileDetailView

## Modify urls: add URL to show one article by pk

from django.urls import path
from .views import ProfileListView, ProfileDetailView

urlpatterns = [
    path("", ProfileListView.as_view(), name="show_all_profiles"),
    path("profile/<int:pk>", ProfileDetailView.as_view(), name="show_profile"),
]
 
