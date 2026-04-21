# mini_insta/serializers.py , Blaise Scileppi (blaises@bu.edu), April 2026
# DRF serializers for the mini_insta REST API

from rest_framework import serializers
from .models import Profile, Post, Photo


class PhotoSerializer(serializers.ModelSerializer):
    # get the right url whether it's a url field or uploaded file
    image = serializers.SerializerMethodField()

    class Meta:
        model = Photo
        fields = ['id', 'image_url', 'image_file', 'image']

    def get_image(self, obj):
        return obj.get_image_url()


class PostSerializer(serializers.ModelSerializer):
    photos = PhotoSerializer(many=True, read_only=True, source='photo_set')
    profile_username = serializers.CharField(source='profile.username', read_only=True)
    profile_display_name = serializers.CharField(source='profile.display_name', read_only=True)
    num_likes = serializers.IntegerField(source='get_num_likes', read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'profile', 'profile_username', 'profile_display_name',
                  'caption', 'timestamp', 'photos', 'num_likes']


class ProfileSerializer(serializers.ModelSerializer):
    num_followers = serializers.IntegerField(source='get_num_followers', read_only=True)
    num_following = serializers.IntegerField(source='get_num_following', read_only=True)

    class Meta:
        model = Profile
        fields = ['id', 'username', 'display_name', 'profile_image_url',
                  'bio_text', 'join_date', 'num_followers', 'num_following']
