from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import Job, Application, Profile
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.conf import settings
from django.contrib.auth import logout

def employer_or_admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('admin-login')
        profile = Profile.objects.filter(user=request.user).first()
        if not profile or profile.user_type not in ['admin', 'employer']:
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper

def sign_in(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            profile = Profile.objects.filter(user=user).first()
            if profile:
                if profile.user_type == 'admin':
                    return redirect('careerapp:career_dashboard')
                elif profile.user_type == 'employer':
                    return redirect('careerapp:manage_jobs')
            return redirect('careerapp:career_dashboard')
        else:
            messages.error(request, "Invalid username or password")
    return render(request, 'careerapp/SignIn.html')

def sign_up(request):
    return render(request, 'careerapp/signup.html')

def save_registration(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        user_type = request.POST['user_type']
        if password1 != password2:
            messages.error(request, "Passwords do not match!")
            return redirect('careerapp:sign_up')
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect('careerapp:sign_up')
        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()
        messages.success(request, "Account created successfully. Please sign in.")
        return redirect('careerapp:sign_in')
    else:
        return redirect('careerapp:sign_up')

def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            profile = Profile.objects.filter(user=user).first()
            if profile and profile.user_type == 'admin':
                login(request, user)
                return redirect('career_dashboard')
        return render(request, 'careerapp/admin_login.html', {'error': 'Invalid credentials'})
    return render(request, 'careerapp/admin_login.html')

def admin_logout(request):
    storage = messages.get_messages(request)
    storage.used = True
    logout(request)
    return redirect('careerapp:sign_in')

# -------------------------
# User-Facing Views
# -------------------------
def home(request):
    jobs = Job.objects.all()
    applied_jobs = []
    if request.user.is_authenticated:
        applied_jobs = Job.objects.filter(careerapp_applications__applicant=request.user)
    return render(request, 'applications/home.html', {'jobs': jobs, 'applied_jobs': applied_jobs})

@login_required
def apply_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    already_applied = Application.objects.filter(
        job=job, applicant=request.user
    ).exists()
    if already_applied:
        messages.info(request, "You have already applied for this job.")
        return redirect('home')
    if request.method == 'POST':
        resume = request.FILES.get('resume')
        if not resume:
            messages.error(request, "Please upload a resume to apply.")
            return redirect('apply_job', job_id=job.id)
        application = Application.objects.create(
            job=job,
            applicant=request.user,
            resume=resume
        )
        candidate_email = request.user.email
        if candidate_email:
            subject = "Application Submitted Successfully"
            message = f"""
Dear {request.user.first_name or request.user.username},

Your application for "{job.title}" has been successfully submitted.

We will review your profile and contact you if shortlisted.

Thank you for applying!

CareerNest Team
            """
            email = EmailMessage(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [candidate_email],
            )
            if application.resume:
                email.attach_file(application.resume.path)

            try:
                email.send(fail_silently=False)
            except Exception as e:
                print("Email error:", e)
        messages.success(request, "Application submitted successfully!")
        return redirect('home')
    return render(request, 'applications/apply.html', {'job': job})

@login_required
def my_applications(request):
    applications = Application.objects.filter(applicant=request.user)
    return render(request, 'applications/my_applications.html', {'applications': applications})

@login_required
def career_dashboard(request):
    total_jobs = Job.objects.count()
    total_applications = Application.objects.count()
    return render(request, 'careerapp/dashboard.html', {'total_jobs': total_jobs, 'total_applications': total_applications})

@login_required
@employer_or_admin_required
def dashboard(request):
    profile = Profile.objects.filter(user=request.user).first()
    if profile.user_type == 'admin':
        jobs = Job.objects.all()
        applications_count = Application.objects.count()
    else:
        jobs = Job.objects.filter(employer=request.user)
        applications_count = Application.objects.filter(job__employer=request.user).count()
    context = {
        'jobs': jobs,
        'total_jobs': jobs.count(),
        'total_applications': applications_count
    }
    return render(request, 'careerapp/dashboard.html', context)

@login_required
@employer_or_admin_required
def post_job(request):
    if request.method == 'POST':
        Job.objects.create(
            employer=request.user,
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            skills=request.POST.get('skills'),
            location=request.POST.get('location'),
            salary=request.POST.get('salary'),
            job_type=request.POST.get('job_type')
        )
        messages.success(request, "Job posted successfully")
        return redirect('career_dashboard')
    return render(request, 'careerapp/post_job.html')

@login_required
@employer_or_admin_required
def manage_jobs(request):
    profile = Profile.objects.filter(user=request.user).first()
    if profile.user_type == 'admin':
        jobs = Job.objects.all()
    else:
        jobs = Job.objects.filter(employer=request.user)
    return render(request, 'careerapp/manage_jobs.html', {'jobs': jobs})

@login_required
@employer_or_admin_required
def edit_job(request, id):
    profile = Profile.objects.get(user=request.user)
    if profile.user_type == 'admin':
        job = get_object_or_404(Job, id=id)
    else:
        job = get_object_or_404(Job, id=id, employer=request.user)
    if request.method == 'POST':
        job.title = request.POST['title']
        job.description = request.POST['description']
        job.skills = request.POST['skills']
        job.location = request.POST['location']
        job.salary = request.POST['salary']
        job.job_type = request.POST['job_type']
        job.save()
        messages.success(request, "Job updated successfully")
        return redirect('careerapp:manage_jobs')
    return render(request, 'careerapp/edit_job.html', {'job': job})

@login_required
@employer_or_admin_required
def delete_job(request, id):
    profile = Profile.objects.get(user=request.user)
    if profile.user_type == 'admin':
        job = get_object_or_404(Job, id=id)
    else:
        job = get_object_or_404(Job, id=id, employer=request.user)
    job.delete()
    messages.success(request, "Job deleted successfully")
    return redirect('careerapp:manage_jobs')

@login_required
@employer_or_admin_required
def view_applicants(request, job_id):
    profile = Profile.objects.get(user=request.user)
    if profile.user_type == 'admin':
        applications = Application.objects.filter(job_id=job_id)
    else:
        applications = Application.objects.filter(job__id=job_id, job__employer=request.user)
    return render(request, 'careerapp/applicants.html', {'applications': applications})
