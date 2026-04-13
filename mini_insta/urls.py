# File: mini_insta/urls.py
# Author: Blaise Scileppi (blaises@bu.edu), February 10 2026
# Description: Defines URL patterns for the mini_insta application.
# Routes requests to views for displaying all profiles and individual profile detail pages.

## Modify urls: add URL to show one article by pk
 
from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

from .views import (
    ProfileListView, ProfileDetailView, MyProfileView, PostDetailView,
    CreatePostView, UpdateProfileView, DeletePostView, UpdatePostView,
    ShowFollowersDetailView, ShowFollowingDetailView, PostFeedListView,
    SearchView, CreateProfileView, FollowView, UnfollowView, LikeView, UnlikeView,
    api_token, api_profiles, api_profile_detail, api_profile_posts,
    api_profile_feed, api_create_post, api_search_profiles,
    api_follow, api_unfollow,
)

urlpatterns = [
    # REST API endpoints (assignment 10)
    path("api/token", api_token, name="api_token"),
    path("api/profiles/", api_profiles, name="api_profiles"),
    path("api/profiles/<int:pk>/", api_profile_detail, name="api_profile_detail"),
    path("api/profiles/<int:pk>/posts/", api_profile_posts, name="api_profile_posts"),
    path("api/profiles/<int:pk>/feed/", api_profile_feed, name="api_profile_feed"),
    path("api/post/", api_create_post, name="api_create_post"),
    path("api/search/", api_search_profiles, name="api_search_profiles"),
    path("api/profiles/<int:pk>/follow/", api_follow, name="api_follow"),
    path("api/profiles/<int:pk>/unfollow/", api_unfollow, name="api_unfollow"),

    path("", ProfileListView.as_view(), name="show_all_profiles"),

    path("profile/<int:pk>", ProfileDetailView.as_view(), name="show_profile"),
    path("profile", MyProfileView.as_view(), name="my_profile"),
    path("profile/update", UpdateProfileView.as_view(), name="update_profile"),
    path("profile/create_post", CreatePostView.as_view(), name="create_post"),
    path("profile/feed", PostFeedListView.as_view(), name="show_feed"),
    path("profile/search", SearchView.as_view(), name="search"),
    path("profile/create_profile", CreateProfileView.as_view(), name="create_profile"),

    path("profile/<int:pk>/followers/", ShowFollowersDetailView.as_view(), name="show_followers"),
    path("profile/<int:pk>/following/", ShowFollowingDetailView.as_view(), name="show_following"),

    path("post/<int:pk>", PostDetailView.as_view(), name="show_post"),
    path("post/<int:pk>/delete/", DeletePostView.as_view(), name="delete_post"),
    path("post/<int:pk>/update/", UpdatePostView.as_view(), name="update_post"),

    path("profile/<int:pk>/follow", FollowView.as_view(), name="follow"),
    path("profile/<int:pk>/delete_follow", UnfollowView.as_view(), name="delete_follow"),
    path("post/<int:pk>/like", LikeView.as_view(), name="like"),
    path("post/<int:pk>/delete_like", UnlikeView.as_view(), name="delete_like"),

    path(
        "login/",
        auth_views.LoginView.as_view(template_name="mini_insta/login.html"),
        name="login"
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="logout_confirmation"),
        name="logout"
    ),
    path(
        "logged_out/",
        TemplateView.as_view(template_name="mini_insta/logged_out.html"),
        name="logout_confirmation"
    ),
]