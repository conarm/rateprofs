from django.shortcuts import render
from django.http import HttpResponse

# Create your views here. Map these views to URLs in urls.py.
def index(request):
    return HttpResponse("Hello, world. You're at the ratings index!")

def register(request):
    # Allow registration with username, email and password
    return HttpResponse('Not yet implemented')

def login(request):
    # Take a username and password and authorise session
    return HttpResponse('Not yet implemented')

def logout(request):
    # End current session
    return HttpResponse('Not yet implemented')

def list(request):
    # Option 1 on spec
    # View a list of all module instances and the professor(s) teaching each of them
    # Format: Code / Name / Year / Semester / Taught by
    # Multiple lines for multiple professors, separate entries by dashes
    return HttpResponse('Not yet implemented')

def view(request):
    # Option 2 on spec
    # View the rating of all professors
    # Format: The rating of Professor Name (Code) is ***** etc.
    return HttpResponse('Not yet implemented')

def average(request):
    # Option 3 on spec
    # View the average rating of a certain professor in a certain module
    # The rating of Professor Name (Code) in module Module (Code) is ***
    # Params: professorId, moduleCode
    return HttpResponse('Not yet implemented')

def rate(request):
    # Option 4 on spec
    # Rate the teaching of a certain professor in a certain module instance
    # Params: professorId, moduleCode, year, semester, rating
    return HttpResponse('Not yet implemented')
