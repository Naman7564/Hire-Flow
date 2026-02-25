from django.urls import path
from . import views

app_name = 'applications'

urlpatterns = [
    path('apply/<int:job_pk>/', views.apply_to_job, name='apply'),
    path('my/', views.my_applications_view, name='my_applications'),
    path('all/', views.all_applications_view, name='all_applications'),
    path('<int:pk>/update-status/', views.update_application_status, name='update_status'),
    path('candidate/<int:pk>/', views.candidate_detail_view, name='candidate_detail'),
]
