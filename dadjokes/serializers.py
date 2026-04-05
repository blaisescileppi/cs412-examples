from rest_framework import serializers
from .models import Joke, Picture
# serializer: used to convert Django models into JSON format

# Serializer for Joke model
class JokeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Joke
        fields = ['id', 'text', 'contributor', 'created_at']

# Serializer for Picture model
class PictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Picture
        fields = ['id', 'image_url', 'contributor', 'created_at']