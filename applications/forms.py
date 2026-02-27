from django import forms
from .models import Application


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['cover_letter', 'resume']
        widgets = {
            'cover_letter': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Tell us why you are interested in this position...'
            }),
        }


class ApplicationStatusForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['status', 'hr_notes']
        widgets = {
            'hr_notes': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Add internal notes...'
            }),
        }


class InterviewScheduleForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['interview_scheduled_at', 'interview_meeting_link', 'interview_notes']
        widgets = {
            'interview_scheduled_at': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control',
                'required': True,
            }),
            'interview_meeting_link': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://zoom.us/j/...',
                'required': True,
            }),
            'interview_notes': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Instructions for the candidate (e.g., what to prepare, who they will meet)...',
            }),
        }
        labels = {
            'interview_scheduled_at': 'Interview Date & Time',
            'interview_meeting_link': 'Meeting Link',
            'interview_notes': 'Instructions for Candidate',
        }

    def clean_interview_meeting_link(self):
        """Validate meeting link format."""
        url = self.cleaned_data.get('interview_meeting_link')
        if url:
            url_lower = url.lower()
            valid_patterns = [
                'zoom.us', 'meet.google', 'teams.microsoft', 'teams.live',
                'webex', 'skype', 'whereby', 'hangouts.google',
                'http://', 'https://'
            ]
            if not any(pattern in url_lower for pattern in valid_patterns):
                if not url.startswith(('http://', 'https://')):
                    raise forms.ValidationError('Please enter a valid meeting URL starting with http:// or https://')
        return url

    def save(self, commit=True):
        """Save form and auto-detect meeting platform."""
        instance = super().save(commit=False)
        if instance.interview_meeting_link:
            instance.interview_platform = instance.detect_meeting_platform()
        if commit:
            instance.save()
        return instance
