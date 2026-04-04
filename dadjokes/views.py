from django.shortcuts import render, get_object_or_404
from .models import Joke, Picture
import random

# Create your views here.
def home(request):
    jokes = Joke.objects.all()
    pictures = Picture.objects.all()

    joke = random.choice(jokes) if jokes else None
    picture = random.choice(pictures) if pictures else None

    return render(request, 'dadjokes/home.html', {
        'joke': joke,
        'picture': picture,
    })

def random_view(request):
    return home(request)

def jokes_list(request):
    jokes = Joke.objects.all().order_by('-created_at')
    return render(request, 'dadjokes/jokes_list.html', {'jokes': jokes})

def joke_detail(request, pk):
    joke = get_object_or_404(Joke, pk=pk)
    return render(request, 'dadjokes/joke_detail.html', {'joke': joke})

def pictures_list(request):
    pictures = Picture.objects.all().order_by('-created_at')
    return render(request, 'dadjokes/pictures_list.html', {'pictures': pictures})

def picture_detail(request, pk):
    picture = get_object_or_404(Picture, pk=pk)
    return render(request, 'dadjokes/picture_detail.html', {'picture': picture})

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import JokeSerializer, PictureSerializer

@api_view(['GET'])
def api_root(request):
    jokes = Joke.objects.all()
    if not jokes:
        return Response({'error': 'No jokes found'}, status=404)
    joke = random.choice(list(jokes))
    serializer = JokeSerializer(joke)
    return Response(serializer.data)

@api_view(['GET'])
def api_random(request):
    jokes = Joke.objects.all()
    if not jokes:
        return Response({'error': 'No jokes found'}, status=404)
    joke = random.choice(list(jokes))
    serializer = JokeSerializer(joke)
    return Response(serializer.data)

@api_view(['GET', 'POST'])
def api_jokes(request):
    if request.method == 'GET':
        jokes = Joke.objects.all().order_by('-created_at')
        serializer = JokeSerializer(jokes, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = JokeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# REST API VIEWS (like in classex)
@api_view(['GET'])
def api_joke_detail(request, pk):
    joke = get_object_or_404(Joke, pk=pk)
    serializer = JokeSerializer(joke)
    return Response(serializer.data)

@api_view(['GET'])
def api_pictures(request):
    pictures = Picture.objects.all().order_by('-created_at')
    serializer = PictureSerializer(pictures, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def api_picture_detail(request, pk):
    picture = get_object_or_404(Picture, pk=pk)
    serializer = PictureSerializer(picture)
    return Response(serializer.data)

@api_view(['GET'])
def api_random_picture(request):
    pictures = Picture.objects.all()
    if not pictures:
        return Response({'error': 'No pictures found'}, status=404)
    picture = random.choice(list(pictures))
    serializer = PictureSerializer(picture)
    return Response(serializer.data)