from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def employer_required(view_func):

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect("login")

        if not hasattr(request.user, "employerprofile"):
            messages.error(request, "You must create an employer profile first.")
            return redirect("job_list")

        return view_func(request, *args, **kwargs)

    return wrapper



def seeker_required(view_func):

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect("login")

        if not hasattr(request.user, "jobseekerprofile"):
            messages.error(request, "You must create a job seeker profile first.")
            return redirect("job_list")

        return view_func(request, *args, **kwargs)

    return wrapper