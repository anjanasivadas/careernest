from django.urls import path
from careerapp import views
from django.contrib.auth.views import LogoutView
app_name = 'careerapp'

urlpatterns = [
    path('dashboard/', views.career_dashboard, name='career_dashboard'),
    path('post-job/', views.post_job, name='post_job'),
    path('manage-jobs/', views.manage_jobs, name='manage_jobs'),
    path('edit-job/<int:id>/', views.edit_job, name='edit_job'),
    path('delete-job/<int:id>/', views.delete_job, name='delete_job'),
    path('view-applicants/<int:job_id>/', views.view_applicants, name='view_applicants'),
    path('admin-login/', views.admin_login, name='admin-login'),
    path('admin-logout/', views.admin_logout, name='admin-logout'),
    path('sign_in/', views.sign_in, name='sign_in'),
    path('', views.sign_up, name='sign_up'),
    path('save_registration/', views.save_registration, name='save_registration'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('manage_jobs/', views.manage_jobs, name='manage_jobs'),
]