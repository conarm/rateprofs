import random
import string
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from api.models import ModuleInstance, Professor, Rating, ModuleInstanceProfessor, Module
from django.db.models import Avg, Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http.response import JsonResponse

# Return 200 OK on success
# Return 422 Unprocessable Entity with a text/plain reason on fields missing
# Return 422 Unprocessable Entity with a text/plain reason otherwise
@csrf_exempt
@require_http_methods(["POST"])
def register_view(request):
    # Allow registration with username, email and password from POST request
    try:
        # Unpack parameters
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        if not username or not email or not password:
            return HttpResponse("Missing required fields", status=422, content_type="text/plain")
        
        # Check unique constraint on email or username (achieve this complex lookup with the Q object)
        if User.objects.filter(Q(email=email) | Q(username=username)).exists():
            return HttpResponse("A user with the provided credentials already exists", status=422, content_type="text/plain")
        
        # Create user
        user = User.objects.create_user(username, email, password)
        user.save()
        return HttpResponse("Success", status=200, content_type="text/plain")
    except Exception:
        # Fallback error response
        return HttpResponse("Something went wrong", status=422, content_type="text/plain")

# Return 200 OK on success
# Return 404 Not Found with a text/plain reason if incorrect user/pass
# Return 422 Unprocessable Entity with a text/plain reason on fields missing
# Return 422 Unprocessable Entity with a text/plain reason otherwise
@csrf_exempt
@require_http_methods(["POST"])
def login_view(request):
    # Take a username and password and authorise session
    try:
        # Unpack parameters
        username = request.POST['username']
        password = request.POST['password']
        if not username or not password:
            return HttpResponse("Missing required fields", status=422, content_type="text/plain")
        
        # Try to authenticate
        user = authenticate(username=username, password=password)
        if user is None:
            return HttpResponse('The username or password is incorrect', status=404, content_type="text/plain")
        
        # Log in if authenticated
        login(request, user)
        return HttpResponse('Success', status=200, content_type="text/plain")
            
    except Exception:
        # Fallback error response
        return HttpResponse("Something went wrong", status=422, content_type="text/plain")

# Return 200 OK on success
# Return 403 Unauthorised with a text/plain reason on authentication failure
# Return 422 Unprocessable Entity with a text/plain reason otherwise
@csrf_exempt
@require_http_methods(["POST"])
def logout_view(request):
    try:
        if (not request.user.is_authenticated):
            return HttpResponse('User is not authenticated', status=403, content_type="text/plain")
        # End current session
        logout(request)
        return HttpResponse('Success', status=200, content_type="text/plain")
    except Exception:
        # Fallback error response
        return HttpResponse("Something went wrong", status=422, content_type="text/plain")

# Return 200 OK with [{modcode, modname, year, semester, [{taughtbyname}]}] on success
# Return 404 Not Found with a text/plain reason on failure
# Return 422 Unprocessable Entity with a text/plain reason otherwise
@require_http_methods(["GET"])
def list_view(request):
    # Option 1 on spec
    # View a list of all module instances and the professor(s) teaching each of them
    try:
        instances = ModuleInstance.objects.all()
        if not instances.exists():
            return HttpResponse("No module instances found", status=404, content_type="text/plain")
        
        data = []
        for instance in instances:
            data.append({
                "module_code": instance.module.code,
                "module_name": instance.module.name,
                "year": instance.year,
                "semester": instance.semester,
                "taught_by": [professor.name for professor in instance.professors.all()]
            })
        return JsonResponse(data, safe=False, status=200)
    except Exception:
        # Fallback error response
        return HttpResponse("Something went wrong", status=422, content_type="text/plain")

# Return 200 OK with {[profname, profcode, avgrating]} on success
# Return 404 Not Found with text/plain if no professors found
# Return 422 Unprocessable Entity with a text/plain reason otherwise
@require_http_methods(["GET"])
def view_view(request):
    # Option 2 on spec
    # View the rating of all professors
    try:
        professors = Professor.objects.annotate(avg_rating=Avg('moduleinstanceprofessor__rating__rating'))
        if not professors.exists():
            return HttpResponse("No ratings found", status=404, content_type="text/plain")
        
        data = []
        for professor in professors:
            data.append({
                "professor_name": professor.name,
                "professor_code": professor.code,
                "average_rating": round(professor.avg_rating) if professor.avg_rating else None,
            })
        return JsonResponse(data, safe=False, status=200)
    except Exception:
        # Fallback error response
        return HttpResponse("Something went wrong", status=422, content_type="text/plain")

# Return 200 OK with {profname, profcode, modulename, modulecode, rating} on success
# Return 404 Not Found with a text/plain reason on failure
# Return 422 Unprocessable Entity with a text/plain reason on fields missing
# Return 422 Unprocessable Entity with a text/plain reason otherwise
@require_http_methods(["GET"])
def average_view(request):
    # Option 3 on spec
    # View the average rating of a certain professor in a certain module
    # Params: professorCode, moduleCode
    try:
        professor_code = request.GET.get('professor_code')
        module_code = request.GET.get('module_code')
        if not professor_code or not module_code:
                return HttpResponse("Missing required fields", status=422, content_type="text/plain")
        
        # Make an aggregate query - group and average out matching professor/module pairs
        avg_rating = Rating.objects.filter(
            moduleInstanceProfessor__professor__code=professor_code,
            moduleInstanceProfessor__moduleInstance__module__code=module_code
        ).aggregate(avg_rating=Avg('rating'))['avg_rating']

        # Fetch professor and module details
        try:
            professor = Professor.objects.get(code=professor_code)
            module = Module.objects.get(code=module_code)
        except (Professor.DoesNotExist, Module.DoesNotExist):
            return HttpResponse("Professor or module not found", status=404, content_type="text/plain")

        # Handle case where there are no ratings
        
        data = {"professor_name": professor.name, 
                "professor_code": professor.code, 
                "module_name": module.name,
                "module_code": module.code,
                "average_rating": round(avg_rating) if avg_rating else None
        }
        return JsonResponse(data, status=200)
    except Exception:
        # Fallback error response
        return HttpResponse("Something went wrong", status=422, content_type="text/plain")

# Return 201 Created on success
# Return 404 Not Found with a text/plain reason on failure
# Return 403 Unauthorised with a text/plain reason on authentication failure
# Return 400 Bad Request if rating isn't numerical
# Return 422 Unprocessable Entity with a text/plain reason on fields missing
# Return 422 Unprocessable Entity with a text/plain reason otherwise
@csrf_exempt
@require_http_methods(["POST"])
def rate_view(request):
    # Option 4 on spec
    # Rate the teaching of a certain professor in a certain module instance
    # Params: professorCode, moduleCode, year, semester, rating
    try:
        if (not request.user.is_authenticated):
            return HttpResponse('User is not authenticated', status=403, content_type="text/plain")
        
        # Unpack parameters
        professorCode = request.POST['professorCode']
        moduleCode = request.POST['moduleCode']
        year = request.POST['year']
        semester = request.POST['semester']
        rating = request.POST['rating']
        if not professorCode or not moduleCode or not year or not semester or not rating:
                return HttpResponse("Missing required fields", status=422, content_type="text/plain")
        
        # Validate and clean parameters
        try:
            # Only validate rating for rounding - others will just cause a moduleInstance not to be found
            rating = round(float(rating))
        except TypeError:
            return HttpResponse('Provided rating is not a number', status=400, content_type="text/plain")
        
        # Search for module instance using parameters
        moduleInstanceProfessor = ModuleInstanceProfessor.objects.filter(
            moduleInstance__module__code=moduleCode,
            moduleInstance__year=year,
            moduleInstance__semester=semester,
            professor__code=professorCode
        ).first()
        
        # Error if module instance not found
        if (moduleInstanceProfessor is None):
            return HttpResponse('Module instance not found', status=404, content_type="text/plain")
        
        # Search for existing ratings for the found module instance
        existingRating = Rating.objects.filter(
            user=request.user.id,
            moduleInstanceProfessor=moduleInstanceProfessor.id,
        ).first()
        
        # Error if an existing rating is found
        if (existingRating is not None):
            return HttpResponse('User has already rated this Module Instance', status=422, content_type="text/plain")
        
        # Create rating
        rating = Rating(user=request.user, moduleInstanceProfessor=moduleInstanceProfessor, rating=request.POST['rating'])
        rating.save()
        return HttpResponse('Added rating', status=200, content_type="text/plain")
    except Exception:
        # Fallback error response
        return HttpResponse("Something went wrong", status=422, content_type="text/plain")