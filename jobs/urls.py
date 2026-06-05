from django.urls import path
from . import views



urlpatterns = [
    path('', views.home_view, name='home'),
    path('job/create/', views.create_job_view, name='create_job'),
    path('job/<int:pk>/edit/', views.edit_job_view, name='edit_job'),
    path('job/<int:pk>/delete/', views.delete_job_view, name='delete_job'),
    path('search/', views.search_view, name='search'),
    path('job/<int:pk>/apply/', views.apply_view, name='apply'),
    path('employer/dashboard/', views.employer_dashboard, name='employer_dashboard'),
    path('applications/', views.applications_view, name='applications'),
]
