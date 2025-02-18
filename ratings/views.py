import random
import string
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from ratings.models import ModuleInstance, Professor, Rating, ModuleInstanceProfessor, Module
from django.db.models import Avg

# Create your views here. Map these views to URLs in urls.py.
# @csrf_exempt # Disable CSRF protection so POSTs can be sent...
def index(request):
    return HttpResponse("Hello, world. You're at the ratings index!")

def seed(request):
    # Seed the database with a professor, module, two users and two ratings
    user1 = User.objects.create_user(username=''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8)), email='test@test.com', password='password')
    user1.save()
    user2 = User.objects.create_user(username=''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8)), email='test@test.com', password='password')
    user2.save()
    
    professor = Professor(name='Roy Ruddle', code='RR')
    professor.save()
    module = Module(name='Info Vis', code='IV')
    module.save()
    moduleInstance = ModuleInstance(module=module, year=2024, semester=1)
    moduleInstance.save()
    moduleInstanceProfessor = ModuleInstanceProfessor(moduleInstance=moduleInstance, professor=professor)
    moduleInstanceProfessor.save()
    
    rating1 = Rating(user=user1, moduleInstanceProfessor=moduleInstanceProfessor, rating=1)
    rating1.save()
    rating2 = Rating(user=user2, moduleInstanceProfessor=moduleInstanceProfessor, rating=5)
    rating2.save()
    
    return HttpResponse('Seeded')

def register(request):
    # Allow registration with username, email and password from POST request
    user = User.objects.create_user(request.POST.get('username'), request.POST.get('email'), request.POST.get('password'))
    user.save()
    return HttpResponse('Not yet implemented')

def login(request):
    # Take a username and password and authorise session
    user = authenticate(username=request.POST.get('username'), password=request.POST.get('password'))
    if user is not None:
        # A backend authenticated the credentials
        return HttpResponse('Authorised but not implemented')
    else:
        return HttpResponse('Unauthorized but not implemented')

def logout(request):
    # End current session
    return HttpResponse('Not yet implemented')

def list(request):
    # Option 1 on spec
    # View a list of all module instances and the professor(s) teaching each of them
    # Format: Code / Name / Year / Semester / Taught by
    # Multiple lines for multiple professors, separate entries by dashes
    table = 'Code | Name | Year | Semester | Taught by<br>'
    instances = ModuleInstance.objects.all()
    for instance in instances:
        for professor in instance.professors.all():
            table += f'{instance.module.code} | {instance.module.name} | {instance.year} | {instance.semester} | {professor.name}<br>'
    return HttpResponse(table)

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
