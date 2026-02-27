from django.urls import path
from . import views

app_name = 'applications'

urlpatterns = [
    path('apply/<int:job_pk>/', views.apply_to_job, name='apply'),
    path('my/', views.my_applications_view, name='my_applications'),
    path('all/', views.all_applications_view, name='all_applications'),
    path('<int:pk>/update-status/', views.update_application_status, name='update_status'),
    path('candidate/<int:pk>/', views.candidate_detail_view, name='candidate_detail'),
    
    # Interview management
    path('interviews/', views.interview_list_view, name='interview_list'),
    path('<int:pk>/schedule-interview/', views.schedule_interview_view, name='schedule_interview'),
    path('<int:pk>/send-notification/', views.send_interview_notification, name='send_notification'),
    path('my-interview/<int:pk>/', views.candidate_interview_view, name='my_interview'),
    
    # Notifications
    path('notifications/', views.notification_list_view, name='notifications'),
    path('notifications/<int:pk>/read/', views.mark_notification_read, name='mark_read'),
    path('notifications/unread-count/', views.unread_notification_count, name='unread_count'),
]
