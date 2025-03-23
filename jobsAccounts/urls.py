from django.urls import path
from .views import job_execution_data,dashboard_view,index_view,create_job, get_jobs,logout_view,home_view,signup_view, login_view, api_signup, api_login
urlpatterns = [
    path('',                 index_view,        name='index'),
    path('signup/',          signup_view,       name='signup'),
    path('login/',           login_view,        name='login'),
    path('home/',            home_view,         name='home'),
    path('dashboard/',       dashboard_view,    name='dashboard'),
    path('api/signup/',      api_signup,        name='api_signup'),
    path('api/login/',       api_login,         name='api_login'),
    path('api/job_execution_data/', job_execution_data, name='job_execution_data'),
    path('api/jobs/',        get_jobs,          name='get_jobs'),  # Fetch jobs from DB
    path('api/jobs/create/', create_job,        name='create_job'),  # Submit job to DB
    path("logout/",          logout_view,       name="logout"),
]
