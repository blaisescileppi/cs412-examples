# File: mini_insta/urls.py
# Author: Blaise Scileppi (blaises@bu.edu), February 10 2026
# Description: Defines URL patterns for the mini_insta application.
# Routes requests to views for displaying all profiles and individual profile detail pages.

## Modify urls: add URL to show one article by pk

from django.urls import path
from .views import ProfileListView, ProfileDetailView, PostDetailView, CreatePostView, UpdateProfileView, DeletePostView, UpdatePostView, ShowFollowersDetailView, ShowFollowingDetailView, PostFeedListView, SearchView

urlpatterns = [
    path("", ProfileListView.as_view(), name="show_all_profiles"),
    path("profile/<int:pk>", ProfileDetailView.as_view(), name="show_profile"),
    path('post/<int:pk>', PostDetailView.as_view(), name='show_post'),
    path('profile/<int:pk>/create_post', CreatePostView.as_view(), name='create_post'),
    path('profile/<int:pk>/update/', UpdateProfileView.as_view(), name='update_profile'),
    path('post/<int:pk>/delete/', DeletePostView.as_view(), name='delete_post'),
    path('post/<int:pk>/update/', UpdatePostView.as_view(), name='update_post'),
    path('profile/<int:pk>/followers/', ShowFollowersDetailView.as_view(), name='show_followers'),
    path('profile/<int:pk>/following/', ShowFollowingDetailView.as_view(), name='show_following'),
    path('profile/<int:pk>/feed', PostFeedListView.as_view(), name='show_feed'),
    path('profile/<int:pk>/search', SearchView.as_view(), name='search'),
]
 
