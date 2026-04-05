## file: quotes/views.py
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
import random
 
 
# Create your views here.
# The application will contain two Python lists in the global scope of the views.py file:
# a list of quotes (string), and a list of images (image URLs, as strings).
# Create both of these lists first, with 3 items in each list. You will add more later.

QUOTES = [
    "'If I find in myself a desire which no experience in this world can satisfy, the most probable explanation is that I was made for another world' - C.S. Lewis",
    "'True humility is not thinking less of yourself; it is thinking of yourself less' - C.S. Lewis",
    "'The task of the modern educator is not to cut down jungles, but to irrigate deserts.' - C.S. Lewis in 'The Abolition of Man'",
]

IMAGES = [
    "https://cdn.britannica.com/24/82724-050-A1F9D0B9/CS-Lewis.jpg",
    "https://upload.wikimedia.org/wikipedia/commons/2/27/CS_Lewis_photo_on_dust_jacket.jpg",
    "https://cdn.shopify.com/s/files/1/1185/0798/files/CS-Lewis-7.jpg",
]
 
 
def home(request):
    '''
    home.
    '''
 
    response_text = '''
    <html>
    <h1>Hello, world!</h1>
 
 
    </html>
    '''
    
    return HttpResponse(response_text)

def quote(request):
    '''
    Main page and task is to randomize a quote and an image.
    Send in context, render quotes.html.
    '''

    template_name = 'quotes/quote.html'
    # a dictionary of context variables (key-value pairs)
    context = {
        "quote": random.choice(QUOTES),
        "image": random.choice(IMAGES),
    }
    return render(request, template_name, context)

def show_all(request):
    '''
    View: show_all
    An ancillary page which will show all quotes and images 
    '''
    template_name = 'quotes/show_all.html'
    
    context = {
        "quotes": QUOTES,
        "images": IMAGES,
    }
    return render(request, template_name, context)


def about(request):
    '''
    View: about
    An about page with short biographical information about the person whose quotes you are displaying.
    A note about the creator of this web application (you)
    '''
    return render(request, "quotes/about.html")