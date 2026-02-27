from django.db import models
from django.conf import settings
from jobs.models import Job


class Application(models.Model):
    STATUS_CHOICES = (
        ('applied', 'Applied'),
        ('reviewing', 'Under Review'),
        ('shortlisted', 'Shortlisted'),
        ('interview', 'Interview Scheduled'),
        ('hired', 'Hired'),
        ('rejected', 'Rejected'),
    )

    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    candidate = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='applications')
    cover_letter = models.TextField(blank=True)
    resume = models.FileField(upload_to='application_resumes/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')
    hr_notes = models.TextField(blank=True, help_text='Internal notes visible only to HR')
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Interview fields
    interview_scheduled_at = models.DateTimeField(null=True, blank=True)
    interview_meeting_link = models.URLField(max_length=500, null=True, blank=True)
    interview_platform = models.CharField(max_length=50, null=True, blank=True)
    interview_notes = models.TextField(blank=True, help_text='Instructions visible to candidate')
    interview_notified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-applied_at']
        unique_together = ['job', 'candidate']

    def __str__(self):
        return f"{self.candidate.get_full_name() or self.candidate.username} → {self.job.title}"

    @property
    def status_color(self):
        colors = {
            'applied': '#6366f1',
            'reviewing': '#f59e0b',
            'shortlisted': '#3b82f6',
            'interview': '#8b5cf6',
            'hired': '#10b981',
            'rejected': '#ef4444',
        }
        return colors.get(self.status, '#6b7280')

    def detect_meeting_platform(self):
        """Auto-detect meeting platform from URL."""
        if not self.interview_meeting_link:
            return None
        url = self.interview_meeting_link.lower()
        platforms = {
            'zoom.us': 'Zoom',
            'meet.google': 'Google Meet',
            'teams.microsoft': 'Microsoft Teams',
            'teams.live': 'Microsoft Teams',
            'webex': 'Webex',
            'skype': 'Skype',
            'whereby': 'Whereby',
        }
        for pattern, name in platforms.items():
            if pattern in url:
                return name
        return 'Other'

    @property
    def has_interview_scheduled(self):
        """Check if interview is scheduled with meeting link."""
        return bool(self.interview_scheduled_at and self.interview_meeting_link)


class Notification(models.Model):
    TYPES = (
        ('interview_scheduled', 'Interview Scheduled'),
        ('interview_updated', 'Interview Updated'),
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='notifications'
    )
    application = models.ForeignKey(
        Application, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='notifications'
    )
    notification_type = models.CharField(max_length=30, choices=TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.user.username}"

    def mark_as_read(self):
        """Mark notification as read."""
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=['is_read'])
