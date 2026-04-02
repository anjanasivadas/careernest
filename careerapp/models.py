from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=20, choices=[
        ('admin', 'Admin'),
        ('employer', 'Employer')
    ])

    def __str__(self):
        return str(self.user)

    @property
    def is_employer(self):
        return self.user_type == 'employer'

class Job(models.Model):
    employer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='jobs_posted')
    title = models.CharField(max_length=200)
    description = models.TextField()
    skills = models.CharField(max_length=200)
    location = models.CharField(max_length=100)
    salary = models.IntegerField(null=True, blank=True)
    job_type = models.CharField(max_length=50, choices=[
        ('Full-time', 'Full-time'),
        ('Part-time', 'Part-time'),
        ('Internship', 'Internship')
    ])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']

def resume_upload_path(instance, filename):
    return f"resumes/{instance.applicant.id}_{instance.job.id}_{filename}"

class Application(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='careerapp_applications')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='careerapp_applications_user')
    resume = models.FileField(upload_to=resume_upload_path)
    status = models.CharField(max_length=20, choices=[
        ('Pending', 'Pending'),
        ('Shortlisted', 'Shortlisted'),
        ('Rejected', 'Rejected')
    ], default='Pending')
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('job', 'applicant')
        ordering = ['-applied_at']

    def __str__(self):
        return f"{self.applicant} - {self.job}"