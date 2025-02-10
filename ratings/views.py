from django.shortcuts import render
from django.http import HttpResponse

# Create your views here. Map these views to URLs in urls.py.
def index(request):
    return HttpResponse("Hello, world. You're at the ratings index!")
