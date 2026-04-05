# formdata/views.py
# view functions to handle URL requests
from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def show_form(request):
    '''Show the web page with the form.'''
 
    template_name = "formdata/form.html"
    return render(request, template_name)

def submit(request):
    '''Process the form submission, generate a result'''

    print(request.POST)

    template_name = "formdata/confirmation.html"
    # Check if POST data was sent with HTTP POST message
    if request.POST:
    # extract form variables
     name = request.POST['name']
     favorite_color = request.POST['favorite_color']

     # provide context variables for use in the template
     context = {
        'name': name, 
        'favorite_color': favorite_color,
     }

    #delegate the response to the template, provide context variables
    return render(request, template_name=template_name, context=context)