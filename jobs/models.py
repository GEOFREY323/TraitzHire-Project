from django.db import models

# Create your models here.
class JobSeekerProfile(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    bio = models.TextField()
    location = models.CharField(max_length=100)
    avatar = models.ImageField(upload_to='Profile_pics/',blank=True, null=True)
    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return '/static/images/default_avatar.png'
    cv = models.FileField(upload_to='cvs/', blank=True, null=True)
    linkin_url = models.URLField(blank=True, null=True)
    portfolio_url = models.URLField(blank=True, null=True)
    skills = models.ManyToManyField('Skill')
    is_open_to_work = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.full_name

class EmployerProfile(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE)
    company_name = models.CharField(max_length=100)
    description = models.TextField()
    website_url = models.URLField(blank=True, null=True)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True, default='company_logos/default_avatar.png')
    location = models.CharField(max_length=100)
    company_size = models.CharField(max_length=100, blank=True, null=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.company_name

class Skill(models.Model):
    name = models.CharField(unique=True, max_length=100)
    slug = models.SlugField(unique=True, max_length=100)

    def __str__(self):
        return self.name

class JobCategory(models.Model):
    name = models.CharField(unique=True, max_length=100)
    slug = models.SlugField(unique=True, max_length=100)
    icon = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name

class Job(models.Model):
    employer = models.ForeignKey(EmployerProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=2000)
    requirements = models.TextField(max_length=1000)
    category = models.ForeignKey(JobCategory, on_delete=models.SET_NULL, null=True)
    skills_required = models.ManyToManyField(Skill, blank=True)
    job_type = models.CharField(max_length=50, choices=[('full-time', 'Full Time'), ('part-time', 'Part Time'), ('remote', 'Remote'), ('contract', 'Contract')])
    location = models.CharField(max_length=100)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    deadline = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    views_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

class Application(models.Model):
    job = models.ForeignKey(Job,on_delete=models.CASCADE,related_name='applications')
    applicant = models.ForeignKey(JobSeekerProfile, on_delete=models.CASCADE)
    cover_letter = models.TextField(max_length=2000, blank=True, null=True)
    cv = models.FileField(upload_to='applications_cvs/')
    status = models.CharField(
        max_length=50,
        choices=[
            ('pending', 'Pending'),
            ('reviewed', 'Reviewed'),
            ('shortlisted', 'Shortlisted'),
            ('rejected', 'Rejected'),
            ('hired', 'Hired')
        ],
        default='pending'
    )
    applied_at = models.DateTimeField(auto_now_add=True)
    employer_notes = models.TextField(max_length=2000, blank=True, null=True)
    class Meta:
        unique_together = ("job", "applicant")
    def __str__(self):
        return f"{self.applicant.full_name} - {self.job.title}"

class SavedJob(models.Model):
    user = models.ForeignKey(JobSeekerProfile, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('user', 'job')
        ordering = ['-saved_at']
    def __str__(self):
        return f"{self.user.full_name} saved {self.job.title}"

class Notification(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    link = models.URLField(blank=True, null=True)
    
    def __str__(self):
        return f"Notification for {self.user.username}"