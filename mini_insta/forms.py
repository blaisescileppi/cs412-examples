# File: forms.py
# Author: Blaise Scileppi (blaises@bu.edu), Due 2/20/2026 @ 1159 PM
# Description: CreateView for the mini insta form
from django import forms
from .models import Post, Profile

class CreatePostForm(forms.ModelForm):
    """
    Form used to create a new Post.
    """

    image_url = forms.URLField(required=False)

    class Meta:
        model = Post
        fields = ['caption']

class UpdateProfileForm(forms.ModelForm):
    """
    Form to update a Profile.
    Username and join_date are excluded.
    """
    class Meta:
        model = Profile
        fields = ['display_name', 'bio_text', 'profile_image_url']


class CreateProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['display_name', 'bio_text', 'profile_image_url']