from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from api.models import ModuleInstance, Professor, Rating, ModuleInstanceProfessor, Module
from django.db.models import Avg, Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http.response import JsonResponse

# Register
# Description: Allow registration with username, email and password from POST request
# Return 200 OK on success
# Return 422 Unprocessable Entity with a text/plain reason on fields missing
# Return 422 Unprocessable Entity with a text/plain reason otherwise
@csrf_exempt
@require_http_methods(["POST"])
def register_view(request):
    try:
        # Unpack parameters
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        if not username or not email or not password:
            return HttpResponse("Missing required fields", status=422, content_type="text/plain")
        
        if User.objects.filter(Q(email=email) | Q(username=username)).exists():
            return HttpResponse("A user with the provided credentials already exists", status=422, content_type="text/plain")
        
        # Create user
        user = User.objects.create_user(username, email, password)
        user.save()
        return HttpResponse("Success", status=200, content_type="text/plain")
    except Exception:
        # Fallback error response
        return HttpResponse("Something went wrong", status=422, content_type="text/plain")

# Login
# Description: Take a username and password and authorise session
# Return 200 OK on success
# Return 404 Not Found with a text/plain reason if incorrect user/pass
# Return 422 Unprocessable Entity with a text/plain reason on fields missing
# Return 422 Unprocessable Entity with a text/plain reason otherwise
@csrf_exempt
@require_http_methods(["POST"])
def login_view(request):
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

# Logout
# Description: End a logged-in session
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

# List
# Description: View a list of all module instances and the professor(s) teaching each of them (option 1 on spec)
# Return 200 OK with [{modcode, modname, year, semester, [{taughtbyname}]}] on success
# Return 404 Not Found with a text/plain reason on failure
# Return 422 Unprocessable Entity with a text/plain reason otherwise
@require_http_methods(["GET"])
def list_view(request):
    try:
        # Get all module instances
        instances = ModuleInstance.objects.all()
        if not instances.exists():
            return HttpResponse("No module instances found", status=404, content_type="text/plain")
        
        # Build response
        data = []
        for instance in instances:
            taught_by = []
            for professor in instance.professors.all():
                taught_by.append({
                    "professor_name": professor.name,
                    "professor_code": professor.code
                })
            data.append({
                "module_code": instance.module.code,
                "module_name": instance.module.name,
                "year": instance.year,
                "semester": instance.semester,
                "taught_by": taught_by
            })
        return JsonResponse(data, safe=False, status=200)
    except Exception:
        # Fallback error response
        return HttpResponse("Something went wrong", status=422, content_type="text/plain")

# View
# Description: View the rating of all professors (option 2 on spec)
# Return 200 OK with {[profname, profcode, avgrating]} on success
# Return 404 Not Found with text/plain if no professors found
# Return 422 Unprocessable Entity with a text/plain reason otherwise
@require_http_methods(["GET"])
def view_view(request):
    try:
        # Get average ratings for each professor
        professors = Professor.objects.annotate(avg_rating=Avg('moduleinstanceprofessor__rating__rating'))
        if not professors.exists():
            return HttpResponse("No ratings found", status=404, content_type="text/plain")

         # Build response
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

# Average
# Description: View the average rating of a certain professor in a certain module (option 3 on spec)
# Params: professorCode, moduleCode
# Return 200 OK with {profname, profcode, modulename, modulecode, rating} on success
# Return 404 Not Found with a text/plain reason on failure
# Return 422 Unprocessable Entity with a text/plain reason on fields missing
# Return 422 Unprocessable Entity with a text/plain reason otherwise
@require_http_methods(["GET"])
def average_view(request):
    try:
        # Unpack params
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

        # Build response
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

# Rate
# Description: Rate the teaching of a certain professor in a certain module instance (option 4 on spec)
# Params: professorCode, moduleCode, year, semester, rating
# Return 201 Created on success
# Return 404 Not Found with a text/plain reason on failure
# Return 403 Unauthorised with a text/plain reason on authentication failure
# Return 400 Bad Request if rating isn't numerical
# Return 422 Unprocessable Entity with a text/plain reason on fields missing
# Return 422 Unprocessable Entity with a text/plain reason otherwise
@csrf_exempt
@require_http_methods(["POST"])
def rate_view(request):
    try:
        if (not request.user.is_authenticated):
            return HttpResponse('User is not authenticated', status=403, content_type="text/plain")
        
        # Unpack parameters
        professorCode = request.POST['professor_code']
        moduleCode = request.POST['module_code']
        year = request.POST['year']
        semester = request.POST['semester']
        rating = request.POST['rating']
        if not professorCode or not moduleCode or not year or not semester or not rating:
                return HttpResponse("Missing required fields", status=422, content_type="text/plain")
        
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
        
        if (moduleInstanceProfessor is None):
            return HttpResponse('Module instance not found', status=404, content_type="text/plain")
        
        # Search for existing ratings for the found module instance
        existingRating = Rating.objects.filter(
            user=request.user.id,
            moduleInstanceProfessor=moduleInstanceProfessor.id,
        ).first()
        
        if (existingRating is not None):
            return HttpResponse('User has already rated this Module Instance', status=422, content_type="text/plain")
        
        # Create rating
        rating = Rating(user=request.user, moduleInstanceProfessor=moduleInstanceProfessor, rating=request.POST['rating'])
        rating.save()
        return HttpResponse('Added rating', status=200, content_type="text/plain")
    except Exception:
        # Fallback error response
        return HttpResponse("Something went wrong", status=422, content_type="text/plain")