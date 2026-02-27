from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import Application, Notification
from .forms import ApplicationForm, ApplicationStatusForm, InterviewScheduleForm
from jobs.models import Job
from accounts.models import CandidateProfile


def candidate_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_candidate:
            messages.error(request, 'Only candidates can access this page.')
            return redirect('dashboard:index')
        return view_func(request, *args, **kwargs)
    return wrapper


def hr_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_hr:
            messages.error(request, 'Only HR can access this page.')
            return redirect('dashboard:index')
        return view_func(request, *args, **kwargs)
    return wrapper


@candidate_required
def apply_to_job(request, job_pk):
    """Candidate applies to a job."""
    job = get_object_or_404(Job, pk=job_pk, status='active')

    # Check if already applied
    if Application.objects.filter(job=job, candidate=request.user).exists():
        messages.warning(request, 'You have already applied to this position.')
        return redirect('jobs:detail', pk=job.pk)

    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.candidate = request.user
            application.save()
            messages.success(request, f'Your application for "{job.title}" has been submitted!')
            return redirect('applications:my_applications')
    else:
        form = ApplicationForm()

    return render(request, 'applications/apply.html', {'form': form, 'job': job})


@candidate_required
def my_applications_view(request):
    """View candidate's own applications."""
    applications = Application.objects.filter(candidate=request.user).select_related('job')

    status_filter = request.GET.get('status', '')
    if status_filter:
        applications = applications.filter(status=status_filter)

    context = {
        'applications': applications,
        'status_filter': status_filter,
        'status_choices': Application.STATUS_CHOICES,
    }
    return render(request, 'applications/my_applications.html', context)


@hr_required
def all_applications_view(request):
    """View all applications (HR only)."""
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    skills_filter = request.GET.get('skills', '')
    experience_filter = request.GET.get('experience', '')

    applications = Application.objects.all().select_related(
        'job', 'candidate', 'candidate__candidate_profile'
    )

    if query:
        applications = applications.filter(
            Q(candidate__first_name__icontains=query) |
            Q(candidate__last_name__icontains=query) |
            Q(candidate__email__icontains=query) |
            Q(job__title__icontains=query)
        )
    if status_filter:
        applications = applications.filter(status=status_filter)
    if skills_filter:
        applications = applications.filter(
            candidate__candidate_profile__skills__icontains=skills_filter
        )
    if experience_filter:
        try:
            exp = int(experience_filter)
            applications = applications.filter(
                candidate__candidate_profile__experience_years__gte=exp
            )
        except ValueError:
            pass

    context = {
        'applications': applications,
        'query': query,
        'status_filter': status_filter,
        'skills_filter': skills_filter,
        'experience_filter': experience_filter,
        'status_choices': Application.STATUS_CHOICES,
    }
    return render(request, 'applications/hr_all_applications.html', context)


@hr_required
def update_application_status(request, pk):
    """Update application status (HR only)."""
    application = get_object_or_404(Application, pk=pk)

    if request.method == 'POST':
        form = ApplicationStatusForm(request.POST, instance=application)
        if form.is_valid():
            form.save()
            messages.success(request, f'Application status updated to "{application.get_status_display()}".')
            return redirect('jobs:detail', pk=application.job.pk)
    else:
        form = ApplicationStatusForm(instance=application)

    return render(request, 'applications/update_status.html', {
        'form': form,
        'application': application,
    })


@hr_required
def candidate_detail_view(request, pk):
    """View a candidate's full profile (HR only)."""
    from accounts.models import User
    candidate = get_object_or_404(User, pk=pk, role='candidate')
    profile = getattr(candidate, 'candidate_profile', None)
    applications = Application.objects.filter(candidate=candidate).select_related('job')

    context = {
        'candidate': candidate,
        'profile': profile,
        'applications': applications,
    }
    return render(request, 'applications/candidate_detail.html', context)


# =============================================================================
# Interview Management Views
# =============================================================================

@hr_required
def interview_list_view(request):
    """View all scheduled interviews (HR only)."""
    query = request.GET.get('q', '')
    platform_filter = request.GET.get('platform', '')
    date_filter = request.GET.get('date', '')
    
    # Get applications with interview scheduled or status='interview'
    applications = Application.objects.filter(
        Q(interview_scheduled_at__isnull=False) | Q(status='interview')
    ).select_related('job', 'candidate', 'candidate__candidate_profile').order_by('interview_scheduled_at')
    
    if query:
        applications = applications.filter(
            Q(candidate__first_name__icontains=query) |
            Q(candidate__last_name__icontains=query) |
            Q(candidate__email__icontains=query) |
            Q(job__title__icontains=query)
        )
    
    if platform_filter:
        applications = applications.filter(interview_platform=platform_filter)
    
    if date_filter == 'today':
        today = timezone.now().date()
        applications = applications.filter(interview_scheduled_at__date=today)
    elif date_filter == 'week':
        today = timezone.now().date()
        week_end = today + timezone.timedelta(days=7)
        applications = applications.filter(
            interview_scheduled_at__date__gte=today,
            interview_scheduled_at__date__lte=week_end
        )
    elif date_filter == 'past':
        applications = applications.filter(interview_scheduled_at__lt=timezone.now())
    
    # Stats
    total_scheduled = applications.filter(interview_scheduled_at__isnull=False).count()
    today = timezone.now().date()
    upcoming_today = applications.filter(interview_scheduled_at__date=today).count()
    week_end = today + timezone.timedelta(days=7)
    upcoming_week = applications.filter(
        interview_scheduled_at__date__gte=today,
        interview_scheduled_at__date__lte=week_end
    ).count()
    
    # Get unique platforms for filter
    platforms = Application.objects.filter(
        interview_platform__isnull=False
    ).values_list('interview_platform', flat=True).distinct()
    
    context = {
        'applications': applications,
        'query': query,
        'platform_filter': platform_filter,
        'date_filter': date_filter,
        'platforms': platforms,
        'total_scheduled': total_scheduled,
        'upcoming_today': upcoming_today,
        'upcoming_week': upcoming_week,
    }
    return render(request, 'applications/interview_list.html', context)


@hr_required
def schedule_interview_view(request, pk):
    """Schedule or edit interview for an application (HR only)."""
    application = get_object_or_404(Application, pk=pk)
    is_editing = application.interview_scheduled_at is not None
    
    if request.method == 'POST':
        form = InterviewScheduleForm(request.POST, instance=application)
        if form.is_valid():
            app = form.save()
            # Update status to 'interview' if not already in a later stage
            if app.status in ['applied', 'reviewing', 'shortlisted']:
                app.status = 'interview'
                app.save(update_fields=['status'])
            
            action = 'updated' if is_editing else 'scheduled'
            messages.success(request, f'Interview {action} successfully for {app.candidate.get_full_name()}.')
            return redirect('applications:interview_list')
    else:
        form = InterviewScheduleForm(instance=application)
    
    context = {
        'form': form,
        'application': application,
        'is_editing': is_editing,
    }
    return render(request, 'applications/schedule_interview.html', context)


@hr_required
@require_POST
def send_interview_notification(request, pk):
    """Send interview notification to candidate (AJAX endpoint)."""
    application = get_object_or_404(Application, pk=pk)
    
    if not application.interview_scheduled_at or not application.interview_meeting_link:
        return JsonResponse({
            'success': False,
            'error': 'Interview details are incomplete. Please schedule the interview first.'
        }, status=400)
    
    # Determine notification type
    existing_notification = Notification.objects.filter(
        application=application,
        notification_type__in=['interview_scheduled', 'interview_updated']
    ).exists()
    
    notification_type = 'interview_updated' if existing_notification else 'interview_scheduled'
    
    # Format the interview time
    interview_time = application.interview_scheduled_at.strftime('%B %d, %Y at %I:%M %p')
    
    # Create notification
    Notification.objects.create(
        user=application.candidate,
        application=application,
        notification_type=notification_type,
        title=f'Interview {"Updated" if existing_notification else "Scheduled"}: {application.job.title}',
        message=f'Your interview for the {application.job.title} position has been scheduled for {interview_time}. '
                f'Platform: {application.interview_platform or "Video Call"}. '
                f'{"Additional notes: " + application.interview_notes if application.interview_notes else ""}'
    )
    
    # Update notified timestamp
    application.interview_notified_at = timezone.now()
    application.save(update_fields=['interview_notified_at'])
    
    return JsonResponse({
        'success': True,
        'message': f'Notification sent to {application.candidate.get_full_name()}.',
        'notified_at': application.interview_notified_at.strftime('%b %d, %Y %I:%M %p')
    })


@candidate_required
def candidate_interview_view(request, pk):
    """View interview details for a candidate's application."""
    application = get_object_or_404(
        Application.objects.select_related('job'),
        pk=pk,
        candidate=request.user
    )
    
    if not application.interview_scheduled_at:
        messages.warning(request, 'No interview has been scheduled for this application yet.')
        return redirect('applications:my_applications')
    
    # Mark related notifications as read
    Notification.objects.filter(
        application=application,
        user=request.user,
        is_read=False
    ).update(is_read=True)
    
    context = {
        'application': application,
    }
    return render(request, 'applications/my_interview_detail.html', context)


# =============================================================================
# Notification Views
# =============================================================================

@login_required
def notification_list_view(request):
    """View all notifications for current user."""
    notifications = Notification.objects.filter(user=request.user)
    
    # Mark all as read option
    if request.GET.get('mark_all_read'):
        notifications.filter(is_read=False).update(is_read=True)
        messages.success(request, 'All notifications marked as read.')
        return redirect('applications:notifications')
    
    context = {
        'notifications': notifications,
        'unread_count': notifications.filter(is_read=False).count(),
    }
    return render(request, 'applications/notification_list.html', context)


@login_required
@require_POST
def mark_notification_read(request, pk):
    """Mark a notification as read (AJAX endpoint)."""
    notification = get_object_or_404(Notification, pk=pk, user=request.user)
    notification.mark_as_read()
    
    return JsonResponse({
        'success': True,
        'message': 'Notification marked as read.'
    })


@login_required
def unread_notification_count(request):
    """Get unread notification count (AJAX endpoint)."""
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'count': count})
