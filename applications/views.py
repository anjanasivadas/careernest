from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from careerapp.models import Job, Application, Profile
from django.contrib.auth import logout, login, authenticate
from django.conf import settings
from django.core.mail import EmailMessage

# ---------------------------
# User-Facing Job Portal Views
# ---------------------------
# ======= Sign In =======
def sign_in(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password")
    return render(request, 'careerapp/SignIn.html')


# ======= Sign Up =======
def sign_up(request):
    return render(request, 'careerapp/SignUp.html')

@login_required(login_url='/career/sign_in/')
def home(request):
    profile = Profile.objects.filter(user=request.user).first()
    if profile and profile.user_type != 'candidate':
        return redirect('/careerapp/dashboard/')
    jobs = Job.objects.all()
    return render(request, 'applications/home.html', {'jobs': jobs})

@login_required
def apply_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    already_applied = Application.objects.filter(
        job=job,
        applicant=request.user
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
        if request.user.email:
            subject = "Application Submitted Successfully"
            message = f"""
Hi {request.user.first_name or request.user.username},

Your application for "{job.title}" has been successfully submitted.

We will review your profile and contact you if shortlisted.

CareerNest Team
"""
            email = EmailMessage(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [request.user.email],
            )
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

def user_logout(request):
    storage = messages.get_messages(request)
    storage.used = True
    logout(request)
    return redirect('careerapp:sign_in')
