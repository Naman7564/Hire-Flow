from django.contrib import admin
from .models import Job


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'department', 'job_type', 'experience_level', 'status', 'posted_by', 'created_at']
    list_filter = ['status', 'job_type', 'experience_level', 'department']
    search_fields = ['title', 'description', 'skills_required']
    date_hierarchy = 'created_at'
