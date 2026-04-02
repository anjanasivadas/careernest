from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from careerapp.models import Job, Application, Profile
from django.contrib.auth import logout, login, authenticate
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
            return redirect('home')  # Redirect to applications home after login
        else:
            messages.error(request, "Invalid username or password")
    return render(request, 'applications/sign_in.html')


# ======= Sign Up =======
def sign_up(request):
    return render(request, 'applications/sign_up.html')

@login_required(login_url='/career/sign_in/')
def home(request):
    profile = Profile.objects.filter(user=request.user).first()
    if profile and profile.user_type != 'candidate':
        return redirect('/career/dashboard/')
    jobs = Job.objects.all()
    return render(request, 'applications/home.html', {'jobs': jobs})

# Apply to a job
@login_required
def apply_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    already_applied = Application.objects.filter(job=job, applicant=request.user).exists()
    if already_applied:
        messages.info(request, "You have already applied for this job.")
        return redirect('home')

    if request.method == 'POST':
        resume = request.FILES.get('resume')
        if not resume:
            messages.error(request, "Please upload a resume to apply.")
        else:
            Application.objects.create(job=job, applicant=request.user, resume=resume)
            messages.success(request, "Application submitted successfully!")
            return redirect('home')

    return render(request, 'applications/apply.html', {'job': job})

@login_required
def my_applications(request):
    applications = Application.objects.filter(applicant=request.user)
    return render(request, 'applications/my_applications.html', {'applications': applications})

def user_logout(request):
    logout(request)
    return redirect('home')