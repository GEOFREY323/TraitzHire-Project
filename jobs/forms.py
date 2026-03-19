from django import forms
import os
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Application, JobSeekerProfile, EmployerProfile, Job

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password1",
            "password2",
        ]

class JobSeekerProfileForm(forms.ModelForm):

    skills = forms.ModelMultipleChoiceField(
        queryset=None,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = JobSeekerProfile
        fields = [
            'full_name',
            'bio',
            'location',
            'avatar',
            'cv',
            'linkin_url',
            'portfolio_url',
            'skills',
            'is_open_to_work'
        ]
    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            # 1. Check file size (limit to 2MB)
            max_size = 2 * 1024 * 1024  # 2MB in bytes
            if avatar.size > max_size:
                raise ValidationError(
                    f'Image file too large. Maximum size is 2MB. '
                    f'Your file is {avatar.size // 1024 // 1024:.1f}MB.'
                )
            # 2. Check file extension
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.webp']
            ext = os.path.splitext(avatar.name)[1].lower()
            if ext not in allowed_extensions:
                raise ValidationError(
                    f'Unsupported file type: {ext}. '
                    f'Allowed types: {', '.join(allowed_extensions)}'
                )
        return avatar

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import Skill
        self.fields['skills'].queryset = Skill.objects.all()

class EmployerProfileForm(forms.ModelForm):
    class Meta:
        model = EmployerProfile
        fields = [
            'company_name',
            'description',
            'website_url',
            'location',
            'company_size',
            'logo'
        ]

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = [
            'cover_letter',
            'cv'
        ]

class JobForm(forms.ModelForm):

    skills_required = forms.ModelMultipleChoiceField(
        queryset=None,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Job
        fields = [
            'title',
            'description',
            'requirements',
            'category',
            'skills_required',
            'job_type',
            'location',
            'salary_min',
            'salary_max',
            'deadline',
            'is_active'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import Skill
        self.fields['skills_required'].queryset = Skill.objects.all()