# File: admin.py
# Author: Blaise Scileppi (blaises@bu.edu), Due 2/13/2026 @ 9 PM
# Description: Initializing the admin and specifying names for Profile model

# Register your models here.
from django.contrib import admin
from .models import Profile, Post, Photo, Follow, Comment, Like

admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(Photo)
admin.site.register(Follow)
admin.site.register(Comment)
admin.site.register(Like)