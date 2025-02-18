import json
import random
import string
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from ratings.models import ModuleInstance, Professor, Rating, ModuleInstanceProfessor, Module
from django.db.models import Avg
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

# Create your views here. Map these views to URLs in urls.py.
@require_http_methods(["GET"])
def index_view(request):
    return HttpResponse("Hello, world. You're at the ratings index!")

@require_http_methods(["GET"])
def seed_view(request):
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

@csrf_exempt
@require_http_methods(["POST"])
def register_view(request):
    # Allow registration with username, email and password from POST request
    user = User.objects.create_user(request.POST['username'], request.POST.get['email'], request.POST['password'])
    user.save()
    return HttpResponse('Saved user')

@csrf_exempt
@require_http_methods(["POST"])
def login_view(request):
    if (request.user.is_authenticated):
        return HttpResponse('User is already authenticated')
    # Take a username and password and authorise session
    user = authenticate(username=request.POST.get('username', ''), password=request.POST.get('password', ''))
    if user is not None:
        # A backend authenticated the credentials
        login(request, user)
        return HttpResponse('Logged in')
    else:
        return HttpResponse('The username or password is incorrect')

@csrf_exempt
@require_http_methods(["POST"])
def logout_view(request):
    if (not request.user.is_authenticated):
        return HttpResponse('User is not authenticated')
    # End current session
    logout(request)
    return HttpResponse('Logged out')

@require_http_methods(["GET"])
def list_view(request):
    # Option 1 on spec
    # View a list of all module instances and the professor(s) teaching each of them
    # Format: Code / Name / Year / Semester / Taught by
    # Multiple lines for multiple professors, separate entries by dashes
    
    if (not request.user.is_authenticated):
        return HttpResponse('User is not authenticated')
    
    # TODO: Handle this formatting server-side or client side
    # We could return a list of entries?
    table = 'Code | Name | Year | Semester | Taught by\n'
    instances = ModuleInstance.objects.all()
    for instance in instances:
        for professor in instance.professors.all():
            table += f'{instance.module.code} | {instance.module.name} | {instance.year} | {instance.semester} | {professor.name}\n'
    return HttpResponse(table)

@require_http_methods(["GET"])
def view_view(request):
    # Option 2 on spec
    # View the rating of all professors
    # Format: The rating of Professor Name (Code) is ***** etc.
    
    if (not request.user.is_authenticated):
        return HttpResponse('User is not authenticated')
    
    output = ''
    average_ratings = Professor.objects.annotate(avg_rating=Avg('moduleinstanceprofessor__rating__rating'))
    for prof in average_ratings:
        output += f'The rating of Professor {prof.name} ({prof.code}) is {'*' * round(prof.avg_rating)}\n'
    return HttpResponse(output)

@require_http_methods(["GET"])
def average_view(request):
    # Option 3 on spec
    # View the average rating of a certain professor in a certain module
    # The rating of Professor Name (Code) in module Module (Code) is ***
    # Params: professorCode, moduleCode
    # Get the average rating for the specific professor in the given module
    # TODO: Should we use professor code or professor ID? Same with module - check the spec
    
    if (not request.user.is_authenticated):
        return HttpResponse('User is not authenticated')
    
    professor_code = request.GET.get('professor_code')
    module_code = request.GET.get('module_code')
    
    avg_rating = Rating.objects.filter(
        moduleInstanceProfessor__professor__code=professor_code,
        moduleInstanceProfessor__moduleInstance__module__code=module_code
    ).aggregate(avg_rating=Avg('rating'))['avg_rating']

    # Fetch professor and module details
    try:
        professor = Professor.objects.get(code=professor_code)
        module = Module.objects.get(code=module_code)
    except (Professor.DoesNotExist, Module.DoesNotExist):
        return HttpResponse("Professor or module not found.")

    # Handle case where there are no ratings
    if avg_rating is None:
        return HttpResponse(f"The rating of Professor {professor.name} ({professor.code}) in module {module.name} ({module.code}) is not available yet.")

    # Format the output with stars
    output = f"The rating of Professor {professor.name} ({professor.code}) in module {module.name} ({module.code}) is {'*' * round(avg_rating)}"
    return HttpResponse(output)

@csrf_exempt
@require_http_methods(["POST"])
def rate_view(request):
    # Option 4 on spec
    # Rate the teaching of a certain professor in a certain module instance
    # Params: professorCode, moduleCode, year, semester, rating
    
    if (not request.user.is_authenticated):
        return HttpResponse('User is not authenticated')
    
    # TODO: Get ModuleInstanceProfessor from user's params
    # Query to get the correct ModuleInstanceProfessor
    moduleInstanceProfessor = ModuleInstanceProfessor.objects.filter(
        moduleInstance__module__code=request.POST['moduleCode'],
        moduleInstance__year=request.POST['year'],
        moduleInstance__semester=request.POST['semester'],
        professor__code=request.POST['professorCode']
    ).first() 
    # TODO: Get rid of first() once we set up constraints?
    
    rating = Rating(user=request.user, moduleInstanceProfessor=moduleInstanceProfessor, rating=request.POST['rating'])
    
    return HttpResponse('Added rating')
