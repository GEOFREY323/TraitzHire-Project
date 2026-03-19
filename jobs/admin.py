from django.contrib import admin
from django.contrib import admin
from .models import (
    Job,
    JobSeekerProfile,
    EmployerProfile,
    JobCategory,
    Skill,
    Application,
    SavedJob,
    Notification
)
# Register your models here
admin.site.register(JobCategory)
admin.site.register(Skill)
admin.site.register(SavedJob)
admin.site.register(Notification)

class JobAdmin(admin.ModelAdmin):

    list_display = (
        'title',
        'employer',
        'location',
        'job_type',
        'is_active',
        'created_at'
    )

    list_filter = (
        'job_type',
        'is_active',
        'created_at'
    )

    search_fields = (
        'title',
        'location'
    )

admin.site.register(Job, JobAdmin)

class JobSeekerAdmin(admin.ModelAdmin):

    list_display = (
        'full_name',
        'user',
        'location',
        'is_open_to_work',
        'joined_at'
    )

    search_fields = (
        'full_name',
        'location'
    )

admin.site.register(JobSeekerProfile, JobSeekerAdmin)

class EmployerAdmin(admin.ModelAdmin):

    list_display = (
        'company_name',
        'user',
        'location',
        'is_verified'
    )

    search_fields = (
        'company_name',
        'location'
    )

admin.site.register(EmployerProfile, EmployerAdmin)

class ApplicationAdmin(admin.ModelAdmin):

    list_display = (
        'job',
        'applicant',
        'status',
        'applied_at'
    )

    list_filter = (
        'status',
        'applied_at'
    )

admin.site.register(Application, ApplicationAdmin)