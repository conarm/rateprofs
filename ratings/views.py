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

@require_http_methods(["GET"])
def seed_view(request):
    # Seed the database with a professor, module, two users and two ratings
    user1 = User.objects.create_user(username=''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8)), email='test@test.com', password='password')
    user1.save()
    user2 = User.objects.create_user(username=''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8)), email='test@test.com', password='password')
    user2.save()
    
    # Create 4 professors
    professor1 = Professor(name='Roy Ruddle', code='RR')
    professor1.save()
    professor2 = Professor(name='John Stell', code='JS')
    professor2.save()
    professor3 = Professor(name='Amie Beloe', code='AB')
    professor3.save()
    professor4 = Professor(name='Owen Johnson', code='OJ')
    professor4.save()
    
    # Create IV module
    module1 = Module(name='Info Vis', code='IV')
    module1.save()
    
    # Create IV module
    module2 = Module(name='Data Vis', code='DV')
    module2.save()
    
    # Instantiate IV module twice (2023,1 and 2024, 1)
    moduleInstance1 = ModuleInstance(module=module1, year=2024, semester=1)
    moduleInstance1.save()
    moduleInstance2 = ModuleInstance(module=module1, year=2023, semester=1)
    moduleInstance2.save()
    
    # Instantiate DV module once (2024, 2)
    moduleInstance3 = ModuleInstance(module=module2, year=2024, semester=2)
    moduleInstance3.save()
    
    # Get Roy to teach IV both times
    moduleInstanceProfessor1 = ModuleInstanceProfessor(moduleInstance=moduleInstance1, professor=professor1)
    moduleInstanceProfessor1.save()
    moduleInstanceProfessor2 = ModuleInstanceProfessor(moduleInstance=moduleInstance2, professor=professor1)
    moduleInstanceProfessor2.save()
    
    # Get Owen to teach IV for the first time
    moduleInstanceProfessor1 = ModuleInstanceProfessor(moduleInstance=moduleInstance1, professor=professor2)
    moduleInstanceProfessor1.save()
    
    # Get Roy to teach DV too
    moduleInstanceProfessor3 = ModuleInstanceProfessor(moduleInstance=moduleInstance3, professor=professor1)
    moduleInstanceProfessor3.save()
    
    # Rate Roy with a 1 and a 3, across the 2023 and 2024 IV module respectively
    # IV module average should be 2
    rating1 = Rating(user=user1, moduleInstanceProfessor=moduleInstanceProfessor1, rating=1)
    rating1.save()
    rating2 = Rating(user=user2, moduleInstanceProfessor=moduleInstanceProfessor2, rating=3)
    rating2.save()
    
    # Rate Roy with a 5 on the DV instance
    # Roy professor average should be 3
    # DV module average should be 5
    rating3 = Rating(user=user2, moduleInstanceProfessor=moduleInstanceProfessor3, rating=5)
    rating3.save()
    
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
    # TODO: Handle this formatting server-side or client side - we could return a list of entries? Formatting isn't necessarily our responsibility
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
    output = ''
    average_ratings = Professor.objects.annotate(avg_rating=Avg('moduleinstanceprofessor__rating__rating'))
    
    for prof in average_ratings:
        if (prof.avg_rating is not None):
            output += f'The rating of Professor {prof.name} ({prof.code}) is {'*' * round(prof.avg_rating)}\n'
        else:
            output += f'Nobody rates Professor {prof.name} ({prof.code})\n'
    return HttpResponse(output)

@require_http_methods(["GET"])
def average_view(request):
    # Option 3 on spec
    # View the average rating of a certain professor in a certain module
    # The rating of Professor Name (Code) in module Module (Code) is ***
    # Params: professorCode, moduleCode
    # Get the average rating for the specific professor in the given module    
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
    
    moduleInstanceProfessor = ModuleInstanceProfessor.objects.filter(
        moduleInstance__module__code=request.POST['moduleCode'],
        moduleInstance__year=request.POST['year'],
        moduleInstance__semester=request.POST['semester'],
        professor__code=request.POST['professorCode']
    ).first()    
    rating = Rating(user=request.user, moduleInstanceProfessor=moduleInstanceProfessor, rating=request.POST['rating'])
    
    return HttpResponse('Added rating')
