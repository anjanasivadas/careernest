from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('apply/<int:job_id>/', views.apply_job, name='apply_job'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('login/', views.sign_in, name='sign_in'),
    path('signup/', views.sign_up, name='sign_up'),
    path('logout/', views.user_logout, name='logout'),
]