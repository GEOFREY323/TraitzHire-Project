# TraitzHire

A full-featured job portal web application built with Django, connecting employers with job seekers through a clean, role-based platform. Employers can post and manage job listings, review applicants, and update application statuses — while job seekers can browse, apply, save jobs, and receive skill-matched recommendations.

**Live deployment:** [traitzhire-project-production.up.railway.app](https://traitzhire-project-production.up.railway.app)

---

## Features

### For Job Seekers
- Register and build a detailed profile (bio, location, LinkedIn, portfolio, CV upload)
- Add and manage skills (from a curated list or by typing custom ones)
- Browse and search job listings by keyword, location, job type, and category
- Apply to jobs with a cover letter and CV upload
- Withdraw applications at any time
- Save jobs for later and view them in a dedicated saved jobs list
- Receive skill-matched job recommendations ranked by relevance
- Track all applications and their statuses (Pending, Reviewed, Shortlisted, Rejected, Hired)
- Receive in-app notifications for new matching job postings and application updates
- View public employer profiles

### For Employers
- Register and build a company profile (name, description, website, logo, location, company size)
- Post job listings with full details: title, description, requirements, category, skills, job type, location, salary range, and deadline
- Activate or deactivate job listings at any time
- Edit and delete job postings
- View and manage all applicants per job
- Review individual applicant profiles and downloaded CVs
- Update application statuses with optional employer notes
- Automatically notify matching job seekers when a new job is posted
- View public job seeker profiles

### Platform-Wide
- Role-based access control (employer vs. job seeker) enforced via custom decorators
- Transactional email notifications via SendGrid (welcome email, application received, new applicant alert)
- Media and static file storage via Cloudinary
- Django admin panel with a custom branded interface

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | Django 6.0.3 |
| Language | Python 3.14.2 |
| Database | PostgreSQL (via `psycopg2-binary` + `dj-database-url`) |
| Media & Static Storage | Cloudinary (`django-cloudinary-storage`) |
| Email | SendGrid (`django-anymail`) |
| WSGI Server | Gunicorn |
| Static Files (dev) | WhiteNoise |
| Image Processing | Pillow |
| Configuration | `python-decouple` |
| Deployment | Railway |

---

## Project Structure

```
traitzhire-project/
├── traitzhire_project/        # Django project configuration
│   ├── settings.py            # App settings, database, storage, email config
│   ├── urls.py                # Root URL configuration
│   ├── asgi.py
│   └── wsgi.py
├── jobs/                      # Core application
│   ├── models.py              # Data models (Job, Application, Profiles, etc.)
│   ├── views.py               # All view logic
│   ├── urls.py                # App URL patterns
│   ├── forms.py               # Django forms for all entities
│   ├── decorators.py          # Role-based access decorators
│   ├── utils.py               # Email utility functions
│   ├── admin.py               # Django admin registrations
│   ├── migrations/            # Database migrations
│   └── templates/
│       ├── base.html          # Base layout template
│       ├── jobs/              # All page templates
│       └── emails/            # HTML and plain-text email templates
├── media/                     # Local media uploads (dev only)
├── manage.py
├── requirements.txt
├── runtime.txt                # Python version pin
└── railway.toml               # Railway deployment configuration
```

---

## Data Models

| Model | Description |
|---|---|
| `Skill` | Canonical skill tags (unique name + slug) |
| `JobSeekerProfile` | Extended profile for job seekers, linked 1-to-1 with Django's `User` |
| `EmployerProfile` | Extended profile for employers, linked 1-to-1 with Django's `User` |
| `JobCategory` | Job categories with slugs and optional icons |
| `Job` | Job listing posted by an employer, with type, salary, deadline, and required skills |
| `Application` | A job seeker's application to a job, with status tracking and employer notes |
| `SavedJob` | A job seeker's bookmarked job listing |
| `Notification` | In-app notification for a user, with a read/unread state and optional link |

---

## Local Setup

### Prerequisites

- Python 3.14+
- PostgreSQL (or use SQLite for local development)
- A [Cloudinary](https://cloudinary.com/) account
- A [SendGrid](https://sendgrid.com/) account and API key

### 1. Clone the repository

```bash
git clone https://github.com/GEOFREY323/traitzhire-project.git
cd traitzhire-project
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-django-secret-key
DEBUG=True

# Database (leave blank to use the SQLite fallback during development)
DATABASE_URL=postgres://user:password@localhost:5432/traitzhire

# Cloudinary
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret

# SendGrid
SENDGRID_API_KEY=your-sendgrid-api-key
SERVER_EMAIL=your-verified-sender@example.com
```

> **Note:** `python-decouple` reads from `.env` automatically. Never commit this file to version control.

### 5. Apply database migrations

```bash
python manage.py migrate
```

### 6. Create a superuser (optional, for admin access)

```bash
python manage.py createsuperuser
```

### 7. Run the development server

```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000`.

---

## Environment Variables Reference

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | Yes | Django secret key |
| `DEBUG` | No | Set to `True` for local development (default: `False`) |
| `DATABASE_URL` | Yes (prod) | Full PostgreSQL connection URL |
| `CLOUDINARY_CLOUD_NAME` | Yes | Cloudinary cloud name |
| `CLOUDINARY_API_KEY` | Yes | Cloudinary API key |
| `CLOUDINARY_API_SECRET` | Yes | Cloudinary API secret |
| `SENDGRID_API_KEY` | Yes | SendGrid API key for transactional email |
| `SERVER_EMAIL` | Yes | Verified sender email address |

---

## Key URL Routes

| URL | Description |
|---|---|
| `/` | Home page with latest job listings |
| `/register/` | User registration (choose role: seeker or employer) |
| `/login/` | Login |
| `/jobs/` | Browse all active job listings |
| `/jobs/<id>/` | Job detail page |
| `/jobs/create/` | Create a new job listing (employers only) |
| `/jobs/<id>/apply/` | Apply to a job (seekers only) |
| `/seeker/dashboard/` | Job seeker dashboard |
| `/employer/dashboard/` | Employer dashboard |
| `/recommended-jobs/` | Skill-matched job recommendations |
| `/notifications/` | In-app notifications |
| `/my-applications/` | View all submitted applications |
| `/jobseeker/dashboard/saved_jobs` | Saved jobs list |
| `/admin/` | Django admin panel |

---

## Deployment on Railway

The project is configured for zero-friction deployment on [Railway](https://railway.app).

**`railway.toml`** defines the build and start behaviour:

```toml
[build]
builder = 'RAILPACK'

[deploy]
startCommand = 'python manage.py migrate && gunicorn traitzhire_project.wsgi --log-file -'
restartPolicyType = 'ON_FAILURE'
```

On every deploy, Railway will:
1. Install dependencies from `requirements.txt`
2. Run all pending database migrations automatically
3. Start the application with Gunicorn

Set all required environment variables in the Railway project's **Variables** tab before deploying. The `DATABASE_URL` variable is automatically injected when a Railway PostgreSQL plugin is attached to the project.

---

## Author

**GAM GEOFREY ANKINIMBOM**
[Owner](https://gam-geofrey-ankinimbom-portfolio.netlify.app)

---

## License

This project is proprietary software developed by Gam Geofrey. All rights reserved. Unauthorised copying, distribution, or modification of this codebase without explicit written permission from Gam Geofrey Ankinimbom is strictly prohibited.
