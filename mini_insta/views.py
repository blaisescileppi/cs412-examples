# File: views.py
# Author: Blaise Scileppi (blaises@bu.edu), February 10 2026
# Description: Contains class-based views for the mini_insta application.
# Includes ProfileListView to display all profiles and ProfileDetailView
# to display a single profile using Django generic views.
from .models import Profile, Post, Photo
from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, DetailView
from .models import Profile
from django.urls import reverse
from .forms import CreatePostForm, UpdateProfileForm
from django.views.generic.edit import UpdateView, DeleteView
from django.views.generic import ListView



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
        Attach profile FK and create Photo objects from uploaded files.
        """
        pk = self.kwargs['pk']
        profile = Profile.objects.get(pk=pk)

        # Attach profile to the Post BEFORE saving
        form.instance.profile = profile

        # Save the Post
        response = super().form_valid(form)

        # Handle uploaded files
        files = self.request.FILES.getlist('files')

        for file in files:
            Photo.objects.create(
                post=self.object,
                image_file=file
            )

        return response
    

    def get_success_url(self):
        return reverse('show_post', kwargs={'pk': self.object.pk})

class UpdateProfileView(UpdateView):
    """
    View to update an existing Profile.
    """
    model = Profile
    form_class = UpdateProfileForm
    template_name = "mini_insta/update_profile_form.html"

class DeletePostView(DeleteView):
    """
    View to delete a Post.
    """
    model = Post
    template_name = "mini_insta/delete_post_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = self.object
        context['profile'] = self.object.profile
        return context

    def get_success_url(self):
        return reverse('show_profile', kwargs={'pk': self.object.profile.pk})
    
class UpdatePostView(UpdateView):
    """
    View to update a Post caption.
    """
    model = Post
    fields = ['caption']
    template_name = "mini_insta/update_post_form.html"

    def get_success_url(self):
        return reverse('show_post', kwargs={'pk': self.object.pk})
    

class ShowFollowersDetailView(DetailView):
    model = Profile
    template_name = "mini_insta/show_followers.html"
    context_object_name = "profile"


class ShowFollowingDetailView(DetailView):
    model = Profile
    template_name = "mini_insta/show_following.html"
    context_object_name = "profile"


class PostFeedListView(ListView):
    model = Post
    template_name = "mini_insta/show_feed.html"
    context_object_name = "posts"

    def get_queryset(self):
        profile = Profile.objects.get(pk=self.kwargs['pk'])
        return profile.get_post_feed()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = Profile.objects.get(pk=self.kwargs['pk'])
        return context
    
class SearchView(ListView):
    template_name = "mini_insta/search_results.html"
    context_object_name = "posts"

    def dispatch(self, request, *args, **kwargs):
        if 'query' not in request.GET:
            profile = Profile.objects.get(pk=self.kwargs['pk'])
            return render(request, "mini_insta/search.html", {"profile": profile})
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        query = self.request.GET.get('query')
        return Post.objects.filter(caption__icontains=query)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = Profile.objects.get(pk=self.kwargs['pk'])
        query = self.request.GET.get('query')

        context['profile'] = profile
        context['query'] = query
        context['profiles'] = Profile.objects.filter(
            username__icontains=query
        ) | Profile.objects.filter(
            display_name__icontains=query
        ) | Profile.objects.filter(
            bio_text__icontains=query
        )

        return context