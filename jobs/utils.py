import threading
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import send_mail

def send_welcome_email(user):
    try:
        print("📨 Sending email to:", user.email)

        from django.core.mail import get_connection
        connection = get_connection()
        connection.open()
        print("✅ SMTP connection opened")

        subject = f"Welcome to TraitzHire, {user.username}!"

        from django.template.loader import render_to_string
        text_content = render_to_string("emails/welcome.txt", {"user": user})
        html_content = render_to_string("emails/welcome.html", {"user": user})

        from django.core.mail import EmailMultiAlternatives
        from django.conf import settings

        email = EmailMultiAlternatives(
            subject,
            text_content,
            settings.EMAIL_HOST_USER,  # 👈 IMPORTANT
            [user.email]
        )

        email.attach_alternative(html_content, "text/html")

        result = email.send(fail_silently=False)

        print("📊 Send result:", result)

        connection.close()
        print("✅ SMTP connection closed")

    except Exception as e:
        print("❌ Email failed:", str(e))


def send_application_received_email(user, job):
    subject = "Application Received"

    message = f"""
Hi {user.username},

Your application for the position "{job.title}" has been received.

The employer will review your application and contact you if you are shortlisted.

Good luck!

TraitzHire Team
"""

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=True,
    )


def send_new_applicant_email(employer_email, job, applicant_name):
    subject = "New Job Application"

    message = f"""
Hello,

You have received a new application for the job "{job.title}".

Applicant: {applicant_name}

Log in to your dashboard to review the application.

TraitzHire Team
"""

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [employer_email],
        fail_silently=True,
    )