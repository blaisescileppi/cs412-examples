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

    def get_all_posts(self):
        """
        Return all Post objects for this Profile,
        ordered newest first.
        """
        return self.post_set.all().order_by('-timestamp')
    
    def __str__(self):
        """Return a readable string representation of this Profile."""
        return f"{self.username} ({self.display_name})"

class Post(models.Model):
    profile = models.ForeignKey("Profile", on_delete=models.CASCADE)
    caption = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def get_all_photos(self):
        """
        Return all Photo objects for this Post.
        """
        return self.photo_set.all().order_by('timestamp')

    def __str__(self):
        return f"Post by {self.profile.username} at {self.timestamp}"


class Photo(models.Model):
    post = models.ForeignKey("Post", on_delete=models.CASCADE)
    image_url = models.URLField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo for Post {self.post.pk}"
