# File: views.py
# Author: Blaise Scileppi (blaises@bu.edu), February 10 2026
# Description: Contains class-based views for the mini_insta application.
# Includes ProfileListView to display all profiles and ProfileDetailView
# to display a single profile using Django generic views.
from .models import Profile, Post, Photo
from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView
from .models import Profile
from django.urls import reverse
from .forms import CreatePostForm


class ProfileListView(ListView):
    """Displays a list of all Profile objects."""
    model = Profile
    template_name = "mini_insta/show_all_profiles.html"
    context_object_name = "profiles"

class ProfileDetailView(DetailView):
    """Displays a  of all Profile objects."""
    model = Profile
    template_name = "mini_insta/show_profile.html"
    context_object_name = "profile"  

class PostDetailView(DetailView):
    """
    Display a single Post and all its photos.
    """
    model = Post
    template_name = "mini_insta/show_post.html"
    context_object_name = "post"

class CreatePostView(CreateView):
    """
    Create a new Post for a specific Profile.
    """
    form_class = CreatePostForm
    template_name = "mini_insta/create_post_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs['pk']
        profile = Profile.objects.get(pk=pk)
        context['profile'] = profile
        return context

    def form_valid(self, form):
        """
        Attach profile FK + create Photo object.
        """
        pk = self.kwargs['pk']
        profile = Profile.objects.get(pk=pk)

        # attach profile to post
        form.instance.profile = profile
        response = super().form_valid(form)

        # create photo
        image_url = self.request.POST.get('image_url')
        if image_url:
            Photo.objects.create(
                post=self.object,
                image_url=image_url
            )

        return response

    def get_success_url(self):
        return reverse('show_post', kwargs={'pk': self.object.pk})
