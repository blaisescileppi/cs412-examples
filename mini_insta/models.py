# File: models.py
# Author: Blaise Scileppi (blaises@bu.edu), February 10 2026
# Description: Defines the data models for the mini_insta application.
# Includes the Profile model used to store user profile information
# such as username, display name, profile image URL, bio text, and join date.


# Create your models here.
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User

class Profile(models.Model):
    """Represent a Mini Insta user profile."""

    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.TextField(blank=False)
    display_name = models.TextField(blank=False)
    profile_image_url = models.URLField(blank=True)
    bio_text = models.TextField(blank=True)
    join_date = models.DateField(auto_now_add=True)

    def get_all_posts(self):
        return self.post_set.all().order_by('-timestamp')

    def __str__(self):
        return f"{self.username} ({self.display_name})"

    def get_absolute_url(self):
        return reverse('show_profile', kwargs={'pk': self.pk})

    def get_followers(self):
        follows = Follow.objects.filter(profile=self)
        return [f.follower_profile for f in follows]

    def get_num_followers(self):
        return len(self.get_followers())

    def get_following(self):
        follows = Follow.objects.filter(follower_profile=self)
        return [f.profile for f in follows]

    def get_num_following(self):
        return len(self.get_following())

    def get_post_feed(self):
        following_profiles = Follow.objects.filter(
            follower_profile=self
        ).values_list('profile', flat=True)

        return Post.objects.filter(
            profile__in=following_profiles
        ).order_by('-timestamp')

class Post(models.Model):
    profile = models.ForeignKey("Profile", on_delete=models.CASCADE)
    caption = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def get_all_photos(self):
        """
        Return all Photo objects for this Post.
        """
        return Photo.objects.filter(post=self)

    def __str__(self):
        return f"Post by {self.profile.username} at {self.timestamp}"
    
    def get_all_comments(self):
        return Comment.objects.filter(post=self).order_by('-timestamp')
    
    def get_likes(self):
        return Like.objects.filter(post=self)

    def get_num_likes(self):
        return self.get_likes().count()

class Photo(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    image_url = models.URLField(blank=True)
    image_file = models.ImageField(upload_to='photos/', blank=True, null=True)

    # def __str__(self):
    #     return f"Photo for Post {self.post.pk}"

    def get_image_url(self):
        """
        Return the correct URL for this image.
        Uses image_url if it exists,
        otherwise uses image_file.
        """
        if self.image_url:
            return self.image_url
        elif self.image_file:
            return self.image_file.url
        return ""

    def __str__(self):
        if self.image_url:
            return f"Photo: {self.image_url}"
        elif self.image_file:
            return f"Photo file: {self.image_file.name}"
        return "Photo"
    
class Follow(models.Model):
    """
    Represents one Profile following another Profile.
    """

    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='publisher'
    )

    follower_profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='subscriber'
    )

    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.follower_profile.display_name} follows {self.profile.display_name}"
    
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    text = models.TextField()

    def __str__(self):
        return f"{self.profile.display_name}: {self.text[:20]}"
    
class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.profile.display_name} liked post {self.post.pk}"