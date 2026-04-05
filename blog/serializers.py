# blog/serializers.py
# contains one of more Serializer classes for our API

# python object into key value pairs for JSON
from rest_framework import serializers
from .models import *

# serializing from type aticle so lets use a name to match that
class ArticleSerializer(serializers.ModelSerializer):
    '''A Serializer class tto convert an Article form Djaango model instance to JSON for API'''

    class Meta:

        model = Article # what model we want to work with
        # which fields we want to expose in the API; not sure what happens whenwe leave it out
        fields = ['id', 'user', 'text', 'author', 'published', 'image_file']
        