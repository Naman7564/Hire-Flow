from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Job
from .forms import JobForm


def hr_required(view_func):
    """Decorator to restrict access to HR users only."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_hr:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('dashboard:index')
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
def job_list_view(request):
    """View all active jobs (for candidates)."""
    query = request.GET.get('q', '')
    job_type = request.GET.get('type', '')
    experience = request.GET.get('experience', '')
    location = request.GET.get('location', '')

    jobs = Job.objects.filter(status='active')

    if query:
        jobs = jobs.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(skills_required__icontains=query) |
            Q(department__icontains=query)
        )
    if job_type:
        jobs = jobs.filter(job_type=job_type)
    if experience:
        jobs = jobs.filter(experience_level=experience)
    if location:
        jobs = jobs.filter(location__icontains=location)

    context = {
        'jobs': jobs,
        'query': query,
        'job_type': job_type,
        'experience': experience,
        'location': location,
        'job_type_choices': Job.JOB_TYPE_CHOICES,
        'experience_choices': Job.EXPERIENCE_CHOICES,
    }

    if request.user.is_candidate:
        return render(request, 'jobs/candidate_job_list.html', context)
    return render(request, 'jobs/hr_job_list.html', context)


@login_required
def job_detail_view(request, pk):
    """View job details."""
    job = get_object_or_404(Job, pk=pk)

    # Check if candidate already applied
    has_applied = False
    if request.user.is_candidate:
        has_applied = job.applications.filter(candidate=request.user).exists()

    context = {
        'job': job,
        'has_applied': has_applied,
    }

    if request.user.is_hr:
        context['applications'] = job.applications.all().select_related('candidate', 'candidate__candidate_profile')
        return render(request, 'jobs/hr_job_detail.html', context)

    return render(request, 'jobs/candidate_job_detail.html', context)


@hr_required
def job_create_view(request):
    """Create a new job posting (HR only)."""
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = request.user
            job.save()
            messages.success(request, f'Job "{job.title}" has been created successfully.')
            return redirect('jobs:detail', pk=job.pk)
    else:
        form = JobForm()

    return render(request, 'jobs/job_form.html', {'form': form, 'action': 'Create'})


@hr_required
def job_edit_view(request, pk):
    """Edit an existing job posting (HR only)."""
    job = get_object_or_404(Job, pk=pk)

    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, f'Job "{job.title}" has been updated.')
            return redirect('jobs:detail', pk=job.pk)
    else:
        form = JobForm(instance=job)

    return render(request, 'jobs/job_form.html', {'form': form, 'action': 'Edit', 'job': job})


@hr_required
def job_delete_view(request, pk):
    """Delete a job posting (HR only)."""
    job = get_object_or_404(Job, pk=pk)
    if request.method == 'POST':
        title = job.title
        job.delete()
        messages.success(request, f'Job "{title}" has been deleted.')
        return redirect('jobs:list')

    return render(request, 'jobs/job_confirm_delete.html', {'job': job})


@hr_required
def hr_all_jobs_view(request):
    """View all jobs including drafts (HR only)."""
    query = request.GET.get('q', '')
    status = request.GET.get('status', '')

    jobs = Job.objects.all()

    if query:
        jobs = jobs.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(skills_required__icontains=query)
        )
    if status:
        jobs = jobs.filter(status=status)

    context = {
        'jobs': jobs,
        'query': query,
        'status_filter': status,
        'status_choices': Job.STATUS_CHOICES,
    }
    return render(request, 'jobs/hr_job_list.html', context)
