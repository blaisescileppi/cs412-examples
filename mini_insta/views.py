# File: views.py
# Author: Blaise Scileppi (blaises@bu.edu), February 10 2026
# Description: Contains class-based views for the mini_insta application.
# Includes ProfileListView to display all profiles and ProfileDetailView
# to display a single profile using Django generic views.


from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Profile

class ProfileListView(ListView):
    """Displays a list of all Profile objects."""
    model = Profile
    template_name = "mini_insta/show_all_profiles.html"
    context_object_name = "profiles"

class ProfileDetailView(DetailView):
    """Displays a  of all Profile objects."""
    model = Profile
    template_name = "mini_insta/show_profile.html"
    context_object_name = "profile"   # VERY IMPORTANT
