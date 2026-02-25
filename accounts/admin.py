from django.contrib import admin
from .models import User, CandidateProfile


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'is_active']
    list_filter = ['role', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']


@admin.register(CandidateProfile)
class CandidateProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'headline', 'experience_years', 'location']
    list_filter = ['experience_years']
    search_fields = ['user__username', 'user__email', 'skills', 'headline']
