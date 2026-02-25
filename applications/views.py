from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Application
from .forms import ApplicationForm, ApplicationStatusForm
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
