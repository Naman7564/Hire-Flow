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
