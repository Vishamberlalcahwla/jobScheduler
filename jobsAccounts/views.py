from django.contrib.auth.models      import User
from django.contrib.auth             import authenticate, login
from django.shortcuts                import render, redirect
from rest_framework.decorators       import api_view
from rest_framework.response         import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Job
from .serializers import JobSerializer
from django.db.models import Avg, Count
# Create a new job
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_job(request):
    data = request.data
    data['created_by'] = request.user.id  # Assign logged-in user
    serializer = JobSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response({'message': 'Job added successfully!', 'job': serializer.data}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Fetch all jobs
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_jobs(request):
    jobs = Job.objects.all().order_by('-created_at')
    serializer = JobSerializer(jobs, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

# Signup View
def signup_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        if User.objects.filter(username=username).exists():
            return render(request, "signup.html", {"error": "Username already exists!"})
        User.objects.create_user(username=username, password=password)
        return redirect("login")
    return render(request, "signup.html")

def index_view(request):
    return render(request, "index.html")


@csrf_exempt  # Allows logout via JavaScript fetch (optional)
def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect("login")  # Redirect to login page after logout
    return JsonResponse({"error": "Invalid request"}, status=400)

# Home View
@login_required(login_url="login")
def home_view(request):
    return render(request, "home.html")

# Login View
def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("home")  # Redirect to another page after login
        return render(request, "login.html", {"error": "Invalid credentials"})
    return render(request, "login.html")

# API Signup
@api_view(["POST"])
def api_signup(request):
    username = request.data.get("username")
    password = request.data.get("password")
    if User.objects.filter(username=username).exists():
        return Response({"error": "Username already taken"}, status=400)
    user = User.objects.create_user(username=username, password=password)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({"token": token.key})

# API Login
@api_view(["POST"])
def api_login(request):
    username = request.data.get("username")
    password = request.data.get("password")
    user = authenticate(username=username, password=password)
    if user:
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"token": token.key})
    return Response({"error": "Invalid credentials"}, status=400)

# Dashboard View
@login_required(login_url="login")
def dashboard_view(request):
    # Jobs grouped by status
    pending_jobs        = Job.objects.filter(status="Pending")
    in_progress_jobs    = Job.objects.filter(status="In Progress")
    completed_jobs      = Job.objects.filter(status="Completed")
    failed_jobs         = Job.objects.filter(status="Failed")
    
    # Analytics: Average wait time and jobs count per priority
    avg_wait_time = Job.objects.aggregate(avg_wait_time=Avg('average_wait_time'))['avg_wait_time']
    
    # Count of jobs per priority (including all statuses)
    jobs_per_priority = Job.objects.values('priority_level').annotate(job_count=Count('id')).order_by('priority_level')

    All_JOBS = Job.objects.all()

    # Create context for the dashboard
    context = {
        'pending_jobs': pending_jobs,
        'in_progress_jobs': in_progress_jobs,
        'completed_jobs': completed_jobs,
        'failed_jobs': failed_jobs,
        'avg_wait_time': avg_wait_time,
        'jobs_per_priority': jobs_per_priority,
        'all_jobs' : All_JOBS,
    }

    return render(request, 'dashboard.html', context)

@login_required(login_url="login")
def job_execution_data(request):
    """Returns job execution data categorized by job status."""
    # Fetch completed jobs, pending jobs, and failed jobs
    completed_jobs = Job.objects.filter(status="Completed")
    pending_jobs = Job.objects.filter(status="Pending")
    failed_jobs = Job.objects.filter(status="Failed")

    job_data = {
        "completed": {
            "labels": [job.job_name for job in completed_jobs],
            "execution_times": [job.estimated_duration for job in completed_jobs],
        },
        "pending": {
            "labels": [job.job_name for job in pending_jobs],
            "execution_times": [job.estimated_duration for job in pending_jobs],
        },
        "failed": {
            "labels": [job.job_name for job in failed_jobs],
            "execution_times": [job.estimated_duration for job in failed_jobs],
        }
    }
    return JsonResponse(job_data)
