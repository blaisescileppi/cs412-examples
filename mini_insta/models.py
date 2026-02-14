# File: models.py
# Author: Blaise Scileppi (blaises@bu.edu), February 10 2026
# Description: Defines the data models for the mini_insta application.
# Includes the Profile model used to store user profile information
# such as username, display name, profile image URL, bio text, and join date.

from django.db import models

# Create your models here.
from django.db import models

class Profile(models.Model):
    """Represent a Mini Insta user profile."""

    username = models.TextField(blank=False)
    display_name = models.TextField(blank=False)
    profile_image_url = models.URLField(blank=True)
    bio_text = models.TextField(blank=True)
    join_date = models.DateField(auto_now_add=True)

    def __str__(self):
        """Return a readable string representation of this Profile."""
        return f"{self.username} ({self.display_name})"
