from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from jobs.models import Job
from applications.models import Application
from accounts.models import User, CandidateProfile
import json


@login_required
def dashboard_index(request):
    """Main dashboard - routes to HR or Candidate dashboard."""
    if request.user.is_hr:
        return hr_dashboard(request)
    return candidate_dashboard(request)


def hr_dashboard(request):
    """HR Dashboard with analytics."""
    total_jobs = Job.objects.count()
    active_jobs = Job.objects.filter(status='active').count()
    total_applications = Application.objects.count()
    total_candidates = User.objects.filter(role='candidate').count()

    # Pipeline stats
    pipeline_stats = Application.objects.values('status').annotate(
        count=Count('id')
    ).order_by('status')

    pipeline_data = {item['status']: item['count'] for item in pipeline_stats}

    # Recent applications
    recent_applications = Application.objects.select_related(
        'candidate', 'candidate__candidate_profile', 'job'
    ).order_by('-applied_at')[:10]

    # Recent jobs
    recent_jobs = Job.objects.order_by('-created_at')[:5]

    # Jobs with most applications
    top_jobs = Job.objects.annotate(
        app_count=Count('applications')
    ).order_by('-app_count')[:5]

    # Status distribution for chart
    status_labels = ['Applied', 'Under Review', 'Shortlisted', 'Interview', 'Hired', 'Rejected']
    status_keys = ['applied', 'reviewing', 'shortlisted', 'interview', 'hired', 'rejected']
    status_counts = [pipeline_data.get(k, 0) for k in status_keys]

    context = {
        'total_jobs': total_jobs,
        'active_jobs': active_jobs,
        'total_applications': total_applications,
        'total_candidates': total_candidates,
        'pipeline_data': pipeline_data,
        'recent_applications': recent_applications,
        'recent_jobs': recent_jobs,
        'top_jobs': top_jobs,
        'status_labels': json.dumps(status_labels),
        'status_counts': json.dumps(status_counts),
        'hired_count': pipeline_data.get('hired', 0),
        'interview_count': pipeline_data.get('interview', 0),
        'shortlisted_count': pipeline_data.get('shortlisted', 0),
    }
    return render(request, 'dashboard/hr_dashboard.html', context)


def candidate_dashboard(request):
    """Candidate Dashboard."""
    profile, created = CandidateProfile.objects.get_or_create(user=request.user)

    my_applications = Application.objects.filter(
        candidate=request.user
    ).select_related('job').order_by('-applied_at')

    # Application stats
    app_stats = my_applications.values('status').annotate(
        count=Count('id')
    )
    app_data = {item['status']: item['count'] for item in app_stats}

    # Available jobs
    applied_job_ids = my_applications.values_list('job_id', flat=True)
    available_jobs = Job.objects.filter(status='active').exclude(
        id__in=applied_job_ids
    ).order_by('-created_at')[:6]

    context = {
        'profile': profile,
        'my_applications': my_applications[:10],
        'total_applied': my_applications.count(),
        'app_data': app_data,
        'available_jobs': available_jobs,
        'shortlisted_count': app_data.get('shortlisted', 0),
        'interview_count': app_data.get('interview', 0),
        'hired_count': app_data.get('hired', 0),
    }
    return render(request, 'dashboard/candidate_dashboard.html', context)
