# File: forms.py
# Author: Blaise Scileppi (blaises@bu.edu), Due 2/20/2026 @ 1159 PM
# Description: CreateView for the mini insta form
from django import forms
from .models import Post

class CreatePostForm(forms.ModelForm):
    """
    Form used to create a new Post.
    """

    image_url = forms.URLField(required=False)

    class Meta:
        model = Post
        fields = ['caption']
