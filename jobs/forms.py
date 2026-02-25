from django import forms
from .models import Job


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            'title', 'description', 'requirements', 'responsibilities',
            'skills_required', 'job_type', 'experience_level', 'location',
            'salary_min', 'salary_max', 'department', 'status', 'deadline'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'requirements': forms.Textarea(attrs={'rows': 4}),
            'responsibilities': forms.Textarea(attrs={'rows': 4}),
            'skills_required': forms.TextInput(attrs={'placeholder': 'Python, Django, REST APIs...'}),
            'deadline': forms.DateInput(attrs={'type': 'date'}),
            'salary_min': forms.NumberInput(attrs={'placeholder': 'Min salary'}),
            'salary_max': forms.NumberInput(attrs={'placeholder': 'Max salary'}),
        }
