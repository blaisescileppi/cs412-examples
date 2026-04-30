# File: views.py
# Author: Blaise Scileppi (blaises@bu.edu), February 10 2026
# Description: Contains class-based views for the mini_insta application.
# Includes ProfileListView to display all profiles and ProfileDetailView
# to display a single profile using Django generic views.

from .models import Profile, Post, Photo, Follow, Like
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from .forms import CreatePostForm, UpdateProfileForm, CreateProfileForm

# REST API imports
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .serializers import ProfileSerializer, PostSerializer


class UserOwnsProfileMixin(LoginRequiredMixin):
    """Require login and provide helper methods for the logged-in user's profile."""

    def get_login_url(self):
        return reverse('login')

    def get_user_profile(self):
        # return Profile.objects.get(user=self.request.user)
        return Profile.objects.filter(user=self.request.user).first()
    

class ProfileListView(ListView):
    model = Profile
    template_name = "mini_insta/show_all_profiles.html"
    context_object_name = "profiles"


class ProfileDetailView(DetailView):
    model = Profile
    template_name = "mini_insta/show_profile.html"
    context_object_name = "profile"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            user_profile = Profile.objects.filter(user=self.request.user).first()

            if user_profile:
                context["is_following"] = Follow.objects.filter(
                    profile=self.object,
                    follower_profile=user_profile
                ).exists()
            else:
                context["is_following"] = False
        else:
            context["is_following"] = False

        return context
    

class MyProfileView(UserOwnsProfileMixin, DetailView):
    model = Profile
    template_name = "mini_insta/show_profile.html"
    context_object_name = "profile"

    def get_object(self):
        return self.get_user_profile()


class PostDetailView(DetailView):
    model = Post
    template_name = "mini_insta/show_post.html"
    context_object_name = "post"


class CreatePostView(UserOwnsProfileMixin, CreateView):
    form_class = CreatePostForm
    template_name = "mini_insta/create_post_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_user_profile()
        return context

    def form_valid(self, form):
        profile = self.get_user_profile()
        form.instance.profile = profile
        response = super().form_valid(form)

        image_url = form.cleaned_data.get('image_url')
        if image_url:
            Photo.objects.create(post=self.object, image_url=image_url)

        files = self.request.FILES.getlist('files')
        for file in files:
            Photo.objects.create(post=self.object, image_file=file)

        return response

    def get_success_url(self):
        return reverse('show_post', kwargs={'pk': self.object.pk})


class UpdateProfileView(UserOwnsProfileMixin, UpdateView):
    model = Profile
    form_class = UpdateProfileForm
    template_name = "mini_insta/update_profile_form.html"

    def get_object(self):
        return self.get_user_profile()


class DeletePostView(UserOwnsProfileMixin, DeleteView):
    model = Post
    template_name = "mini_insta/delete_post_form.html"

    # def get_queryset(self):
    #         query = self.request.GET.get('query')

    #         if not query:
    #             return Post.objects.none()
    #         return Post.objects.filter(caption__icontains=query)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = self.object
        context['profile'] = self.object.profile
        return context

    def get_success_url(self):
        return reverse('show_profile', kwargs={'pk': self.get_user_profile().pk})
    
    def get_queryset(self):
        profile = self.get_user_profile()
        return Post.objects.filter(profile=profile)


class UpdatePostView(UserOwnsProfileMixin, UpdateView):
    model = Post
    fields = ['caption']
    template_name = "mini_insta/update_post_form.html"

    def get_queryset(self):
        return Post.objects.filter(profile=self.get_user_profile())

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


class PostFeedListView(UserOwnsProfileMixin, ListView):
    model = Post
    template_name = "mini_insta/show_feed.html"
    context_object_name = "posts"

    def get_queryset(self):
        return self.get_user_profile().get_post_feed()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_user_profile()
        return context


class SearchView(UserOwnsProfileMixin, ListView):
    template_name = "mini_insta/search_results.html"
    context_object_name = "posts"

    def dispatch(self, request, *args, **kwargs):
        if 'query' not in request.GET:
            return render(
                request,
                "mini_insta/search.html",
                {"profile": self.get_user_profile()}
            )
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        query = self.request.GET.get('query')
        return Post.objects.filter(caption__icontains=query)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.get_user_profile()
        query = self.request.GET.get('query')

        context['profile'] = profile
        context['query'] = query
        context['profiles'] = (
            Profile.objects.filter(username__icontains=query) |
            Profile.objects.filter(display_name__icontains=query) |
            Profile.objects.filter(bio_text__icontains=query)
        )
        return context


class CreateProfileView(CreateView):
    form_class = CreateProfileForm
    template_name = "mini_insta/create_profile_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_form'] = UserCreationForm()
        return context

    def form_valid(self, form):
        user_form = UserCreationForm(self.request.POST)

        if not user_form.is_valid():
            return self.form_invalid(form)

        user = user_form.save()
        login(self.request, user)
        form.instance.user = user
        form.instance.username = user.username

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('show_profile', kwargs={'pk': self.object.pk})
    
# ADDING LIKES AND FOLLLOWS:
class FollowView(UserOwnsProfileMixin, TemplateView):
    def dispatch(self, request, *args, **kwargs):
        current_profile = self.get_user_profile()
        other_profile = get_object_or_404(Profile, pk=self.kwargs['pk'])

        if current_profile != other_profile:
            Follow.objects.get_or_create(
                profile=other_profile,
                follower_profile=current_profile
            )

        return redirect('show_profile', pk=other_profile.pk)


class UnfollowView(UserOwnsProfileMixin, TemplateView):
    def dispatch(self, request, *args, **kwargs):
        current_profile = self.get_user_profile()
        other_profile = get_object_or_404(Profile, pk=self.kwargs['pk'])

        Follow.objects.filter(
            profile=other_profile,
            follower_profile=current_profile
        ).delete()

        return redirect('show_profile', pk=other_profile.pk)


class LikeView(UserOwnsProfileMixin, TemplateView):
    def dispatch(self, request, *args, **kwargs):
        current_profile = self.get_user_profile()
        post = get_object_or_404(Post, pk=self.kwargs['pk'])

        if post.profile != current_profile:
            Like.objects.get_or_create(post=post, profile=current_profile)

        return redirect('show_post', pk=post.pk)


class UnlikeView(UserOwnsProfileMixin, TemplateView):
    def dispatch(self, request, *args, **kwargs):
        current_profile = self.get_user_profile()
        post = get_object_or_404(Post, pk=self.kwargs['pk'])

        Like.objects.filter(post=post, profile=current_profile).delete()

        return redirect('show_post', pk=post.pk)
    
# REST API views (assignment 10)

@api_view(['POST'])
@permission_classes([AllowAny])
def api_token(request):
    """Login endpoint - returns auth token and profile id."""
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)

    if user is not None:
        token, created = Token.objects.get_or_create(user=user)
        profile = Profile.objects.filter(user=user).first()
        profile_id = profile.pk if profile else None
        return Response({'token': token.key, 'profile_id': profile_id})
    else:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def api_profiles(request):
    """Return list of all profiles."""
    profiles = Profile.objects.all()
    serializer = ProfileSerializer(profiles, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def api_profile_detail(request, pk):
    """Return a single profile."""
    profile = get_object_or_404(Profile, pk=pk)
    serializer = ProfileSerializer(profile)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def api_profile_posts(request, pk):
    """Return all posts for a given profile."""
    profile = get_object_or_404(Profile, pk=pk)
    posts = profile.get_all_posts()
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def api_profile_feed(request, pk):
    """Return the feed for a given profile (posts from people they follow)."""
    profile = get_object_or_404(Profile, pk=pk)
    posts = profile.get_post_feed()
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def api_create_post(request):
    """Create a new post for the logged in user."""
    profile = get_object_or_404(Profile, user=request.user)
    caption = request.data.get('caption', '')
    image_url = request.data.get('image_url', '')

    post = Post.objects.create(profile=profile, caption=caption)

    if image_url:
        Photo.objects.create(post=post, image_url=image_url)

    serializer = PostSerializer(post)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def api_search_profiles(request):
    """Search profiles by username or display name."""
    q = request.GET.get('q', '').strip()
    if not q:
        return Response([])

    my_profile = get_object_or_404(Profile, user=request.user)
    profiles = (
        Profile.objects.filter(username__icontains=q) |
        Profile.objects.filter(display_name__icontains=q)
    ).exclude(pk=my_profile.pk).distinct()

    result = []
    for p in profiles:
        data = ProfileSerializer(p).data
        data['is_following'] = Follow.objects.filter(
            profile=p, follower_profile=my_profile
        ).exists()
        result.append(data)

    return Response(result)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def api_follow(request, pk):
    """Follow another profile."""
    my_profile = get_object_or_404(Profile, user=request.user)
    other_profile = get_object_or_404(Profile, pk=pk)

    if my_profile != other_profile:
        Follow.objects.get_or_create(profile=other_profile, follower_profile=my_profile)

    return Response({'status': 'following'})


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def api_unfollow(request, pk):
    """Unfollow a profile."""
    my_profile = get_object_or_404(Profile, user=request.user)
    other_profile = get_object_or_404(Profile, pk=pk)

    Follow.objects.filter(profile=other_profile, follower_profile=my_profile).delete()

    return Response({'status': 'unfollowed'})
