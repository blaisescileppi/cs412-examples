# File: admin.py
# Author: Blaise Scileppi (blaises@bu.edu), Due 2/13/2026 @ 9 PM
# Description: Initializing the admin and specifying names for Profile model

from django.contrib import admin
from .models import Profile


from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Profile

admin.site.register(Profile)
