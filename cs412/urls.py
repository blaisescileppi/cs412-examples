"""
URL configuration for cs412 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
# """
# file: hw/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static    ## add for static files
from django.conf import settings


urlpatterns = [ 
    path('admin/', admin.site.urls),
    path('hw/', include("hw.urls")),
    path('', include("quotes.urls")), # added for assignment 1
    path('formdata/', include("formdata.urls")), # assignment 2 example
    path('restaurant/', include("restaurant.urls")), # assignment 2
    path('blog/', include("blog.urls")), # assignment 3 example
    path('mini_insta/', include("mini_insta.urls")), # assignment 3
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

