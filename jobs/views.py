import re, os
from django.conf import settings
from django.db import models as db_models
from django.core.mail import send_mail
from django.forms import Form
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .decorators import employer_required, seeker_required
from django.http import JsonResponse
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.contrib.auth.forms import UserCreationForm
from .models import Job, JobCategory, EmployerProfile, JobSeekerProfile, Application, SavedJob, Notification
from .forms import ApplicationForm, JobSeekerProfileForm, EmployerProfileForm, JobForm, RegisterForm
from .utils import send_application_received_email, send_new_applicant_email, send_welcome_email

from .models import JobSeekerProfile, EmployerProfile

from django.contrib.auth import login

import threading
from django.contrib.auth import login

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        role = request.POST.get("role")
        if form.is_valid() and role in ["seeker", "employer"]:
            user = form.save()
            if role == "seeker":
                JobSeekerProfile.objects.get_or_create(user=user)
                redirect_url = "edit_seeker_profile"
            else:
                EmployerProfile.objects.get_or_create(user=user)
                redirect_url = "edit_employer_profile"
            login(request, user)
            # ✅ SEND EMAIL IN BACKGROUND (no timeout)
            threading.Thread(
                target=send_welcome_email,
                args=(user,)
            ).start()
            messages.success(request, "Welcome to TraitzHire!")
            return redirect(redirect_url)
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = RegisterForm()
    return render(request, "jobs/register.html", {"form": form})

@seeker_required
@login_required
def job_list(request):
    jobs = Job.objects.filter(is_active=True)
    keyword = request.GET.get("keyword")
    location = request.GET.get("location")
    job_type = request.GET.get("job_type")
    category = request.GET.get("category")
    if keyword:
        jobs = jobs.filter(
            Q(title__icontains=keyword) |
            Q(description__icontains=keyword)
        )
    if location:
        jobs = jobs.filter(location__icontains=location)
    if job_type:
        jobs = jobs.filter(job_type=job_type)
    if category:
        jobs = jobs.filter(category_id=category)
    categories = JobCategory.objects.all()
    return render(request, "jobs/job_list.html", {
        "jobs": jobs,
        "categories": categories
    })

@seeker_required
@login_required
def apply(request, pk):
    job = get_object_or_404(Job, pk=pk)
    jobseeker = request.user.jobseekerprofile
    # CHECK IF ALREADY APPLIED
    if Application.objects.filter(job=job, applicant=jobseeker).exists():
        messages.warning(request, "You have already applied to this job.")
        return redirect("job_detail", pk=job.pk)
    if request.method == "POST":
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.applicant = jobseeker
            application.job = job
            application.save()
            from .utils import create_notification
            # notify employer
            create_notification(
                user=job.employer.user,
                message=f"{request.user.username} applied for your job '{job.title}'",
                link=f"/applicant/{application.id}/"
            )
            # notify applicant
            create_notification(
                user=request.user,
                message=f"You successfully applied for '{job.title}'",
                link=f"/jobs/{job.id}/"
            )
            # SEND EMAILS
            send_application_received_email(application)
            send_new_applicant_email(application)
            messages.success(request, "Application submitted successfully!")
            return redirect("job_detail", pk=job.pk) 
    else:
        form = ApplicationForm()
    return render(request, "jobs/apply.html", {
        "form": form,
        "job": job
    })

@login_required
@seeker_required
def seeker_dashboard(request):
    jobseeker, created = JobSeekerProfile.objects.get_or_create(
        user=request.user
    )
    applications = Application.objects.filter(
        applicant=jobseeker
    ).select_related(
        'job',
        'job__employer'
    )
    # 🔍 Jobs
    jobs = Job.objects.all().select_related('employer', 'category')
    keyword = request.GET.get("keyword")
    location = request.GET.get("location")
    job_type = request.GET.get("job_type")
    category = request.GET.get("category")
    if keyword:
        jobs = jobs.filter(
            Q(title__icontains=keyword) |
            Q(description__icontains=keyword)
        )
    if location:
        jobs = jobs.filter(location__icontains=location)
    if job_type:
        jobs = jobs.filter(job_type=job_type)
    if category:
        jobs = jobs.filter(category__id=category)
    categories = JobCategory.objects.all()
    context = {
        "applications": applications,
        "jobs": jobs,
        "categories": categories,
        "profile": jobseeker,   # ✅ THIS IS THE FIX
    }
    return render(request, "jobs/seeker_dashboard.html", context)

@login_required
@seeker_required
def edit_seeker_profile(request):
    profile = get_object_or_404(JobSeekerProfile, user=request.user)
    if request.method == 'POST':
        form = JobSeekerProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # Delete old avatar if a new one is uploaded
            if 'avatar' in request.FILES and profile.avatar:
                old_path = profile.avatar.path
                if os.path.isfile(old_path):
                    os.remove(old_path)
            # Save profile without committing M2M yet
            profile = form.save(commit=False)
            profile.save()
            # Save checkbox-selected skills
            form.save_m2m()
            # Handle new typed skills (FIXED COMPLETELY)
            new_skills_input = request.POST.get("new_skills", "")
            if new_skills_input:
                from django.utils.text import slugify
                from .models import Skill
                new_skills_list = [
                    s.strip() for s in new_skills_input.split(",") if s.strip()
                ]
                for skill_name in new_skills_list:
                    # Check existing skill (case-insensitive)
                    skill_obj = Skill.objects.filter(
                        name__iexact=skill_name
                    ).first()
                    # Create only if it doesn't exist
                    if not skill_obj:
                        skill_obj = Skill.objects.create(
                            name=skill_name,
                            slug=slugify(skill_name)
                        )
                    #  Add to profile
                    profile.skills.add(skill_obj)
            messages.success(request, 'Profile updated!')
            return redirect('seeker_dashboard')
    else:
        form = JobSeekerProfileForm(instance=profile)
    return render(request, 'jobs/edit_seeker_profile.html', {'form': form})

@login_required
@employer_required
def employer_dashboard(request):
    employer = request.user.employerprofile
    jobs = Job.objects.filter(employer=employer).prefetch_related(
        'applications__applicant'
    )
    applications = Application.objects.filter(
        job__employer=employer
    ).select_related('applicant__jobseekerprofile', 'job')
    return render(request, 'jobs/employer_dashboard.html', {
        'employer': employer,
        'jobs': jobs,
        'applications': applications,
    })

@login_required
@employer_required
def edit_employer_profile(request):
    profile = get_object_or_404(EmployerProfile, user=request.user)
    if request.method == 'POST':
        form = EmployerProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # Delete old avatar if replaced
            if 'avatar' in request.FILES and profile.avatar:
                old_path = profile.avatar.path
                if os.path.isfile(old_path):
                    os.remove(old_path)
            profile = form.save(commit=False)
            profile.save()
            # Ensure any file fields or related fields are applied
            form.save_m2m()
            messages.success(request, 'Profile updated!')
            return redirect('employer_dashboard')
    else:
        form = EmployerProfileForm(instance=profile)
    return render(request, 'jobs/edit_employer_profile.html', {'form': form})

def public_jobseeker_profile(request, pk):
    profile = get_object_or_404(JobSeekerProfile, pk=pk)
    return render(request, 'jobs/public_jobseeker_profile.html', {'profile': profile})

def public_employer_profile(request, pk):
    employer = get_object_or_404(EmployerProfile, pk=pk)
    jobs = Job.objects.filter(
        employer=employer,
        is_active=True
    )
    return render(
        request,
        "jobs/public_employer_profile.html",
        {
            "employer": employer,
            "jobs": jobs
        }
    )

def job_detail(request, pk):
    job = Job.objects.get(pk=pk)
    is_saved = False
    if request.user.is_authenticated:
        jobseeker = request.user.jobseekerprofile
        is_saved = SavedJob.objects.filter(
            user=jobseeker,
            job=job
        ).exists()
    return render(request, "jobs/job_detail.html", {
        "job": job,
        "is_saved": is_saved
    })
    
@login_required
@employer_required
def create_job(request):
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.employer = request.user.employerprofile
            job.save()

            # ✅ Save selected checkbox skills
            form.save_m2m()

            # ✅ ADD THIS BLOCK (custom skills)
            new_skills_input = request.POST.get("new_skills", "")

            if new_skills_input:
                from django.utils.text import slugify
                from .models import Skill

                new_skills_list = [
                    s.strip() for s in new_skills_input.split(",") if s.strip()
                ]

                for skill_name in new_skills_list:
                    # Check if skill exists (case-insensitive)
                    skill_obj = Skill.objects.filter(
                        name__iexact=skill_name
                    ).first()

                    # Create if not exists
                    if not skill_obj:
                        skill_obj = Skill.objects.create(
                            name=skill_name,
                            slug=slugify(skill_name)
                        )

                    # Add to job
                    job.skills_required.add(skill_obj)

            messages.success(request, 'Job created!')
            return redirect('employer_dashboard')
    else:
        form = JobForm()

    return render(request, 'jobs/create_job.html', {'form': form})

@login_required
@employer_required
def edit_job(request, pk):
    job = get_object_or_404(
        Job,
        pk=pk,
        employer=request.user.employerprofile
    )

    if request.method == 'POST':
        form = JobForm(request.POST, request.FILES, instance=job)

        if form.is_valid():
            job = form.save()  

            new_skills_input = request.POST.get("new_skills", "")

            if new_skills_input:
                from django.utils.text import slugify
                from .models import Skill

                new_skills_list = [
                    s.strip() for s in new_skills_input.split(",") if s.strip()
                ]

                for skill_name in new_skills_list:
                    skill_obj = Skill.objects.filter(
                        name__iexact=skill_name
                    ).first()

                    if not skill_obj:
                        skill_obj = Skill.objects.create(
                            name=skill_name,
                            slug=slugify(skill_name)
                        )

                    job.skills_required.add(skill_obj)

            messages.success(request, 'Job updated!')
            return redirect('employer_dashboard')

    else:
        form = JobForm(instance=job)

    return render(request, 'jobs/edit_job.html', {'form': form, 'job': job})

@login_required
@employer_required
def delete_job(request, pk):
    job = get_object_or_404(
    Job,
    pk=pk,
    employer=request.user.employerprofile)
    if request.method == 'POST':
        job.delete()
        messages.success(request, 'Job deleted!')
        return redirect('employer_dashboard')
    return render(request, 'jobs/confirm_delete.html', {'job': job})

@login_required
@employer_required
def toggle_job(request, pk):
    job = get_object_or_404(
    Job,
    pk=pk,
    employer=request.user.employerprofile
)
    job.is_active = not job.is_active
    job.save()
    status = 'activated' if job.is_active else 'deactivated'
    messages.success(request, f'Job {status}!')
    return redirect('employer_dashboard')


@login_required
@seeker_required
def withdraw_application(request, pk):
    application = get_object_or_404(
    Application,
    pk=pk,
    applicant=request.user.jobseekerprofile
)
    application.delete()
    return redirect("seeker_dashboard")

@login_required
@employer_required
def manage_applicants(request, pk):
    job = get_object_or_404(Job, pk=pk, employer=request.user.employerprofile)
    applications = Application.objects.filter(job=job)
    return render(request, "jobs/manage_applicants.html", {
        'job': job,
        'applications': applications
    })

@login_required
@employer_required
def applicant_detail(request, pk):
    application = get_object_or_404(Application, pk=pk, job__employer=request.user.employerprofile)
    return render(request, "jobs/applicant_detail.html", {'application':application})

@login_required
@employer_required
def update_status(request, pk):
    application = get_object_or_404(Application, pk=pk, job__employer=request.user.employerprofile)
    if request.method == 'POST':
        status = request.POST.get("status")
        application.status=status
        application.save()
    return redirect("manage_applicants", pk=application.job.pk)


# views.py
@login_required
def save_job(request, pk):
    job = get_object_or_404(Job, pk=pk)
    jobseeker = request.user.jobseekerprofile
    saved_job, created = SavedJob.objects.get_or_create(
    user=jobseeker,
    job=job
)
    if not created:
        saved_job.delete()
        messages.info(request, "Job removed from saved jobs.")
    else:
        messages.success(request, "Job saved successfully.")
    return redirect('job_detail', pk=job.id)

@login_required
def saved_jobs(request):
    jobseeker = request.user.jobseekerprofile
    saved_jobs = SavedJob.objects.filter(
        user=jobseeker
    ).select_related('job', 'job__employer')
    return render(request, 'jobs/saved_jobs.html', {
        'saved_jobs': saved_jobs
    })

@login_required
@seeker_required
def recommended_jobs(request):
    jobseeker = request.user.jobseekerprofile
    skills = jobseeker.skills.all()
    jobs = Job.objects.filter(
        is_active=True
    ).annotate(
        match_count=db_models.Count(
            'skills_required',
            filter=db_models.Q(skills_required__in=skills)
        )
    ).order_by('-match_count')
    return render(request, 'jobs/recommended_jobs.html', {
        'jobs': jobs
    })

@login_required(login_url='login')
def notifications(request):
    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')
    return render(request, 'jobs/notifications.html', {
        'notifications': notifications
    })

def home(request):
    jobs = Job.objects.filter(is_active=True).order_by('-created_at')[:6]
    return render(request, "jobs/home.html", {
        "jobs": jobs
    })


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(
            request,
            username=username,
            password=password
        )
        if user is not None:
            login(request, user)
            return redirect("redirect_after_login")
        else:
            messages.error(request, "Invalid username or password")
    return render(request, "jobs/login.html")




def logout_view(request):
    logout(request)
    return redirect("home")


@login_required
def redirect_after_login(request):
    user = request.user
    if hasattr(user, "jobseekerprofile"):
        return redirect("seeker_dashboard")
    if hasattr(user, "employerprofile"):
        return redirect("employer_dashboard")
    return redirect("login")

@login_required
@seeker_required
def my_applications(request):
    applications = Application.objects.filter(
        applicant=request.user.jobseekerprofile
    ).select_related("job")
    return render(request, "jobs/my_applications.html", {
        "applications": applications
    })