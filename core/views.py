from django.shortcuts import render
from courses.models import Course


def home(request):
    courses = Course.objects.filter(is_published=True).order_by("-created_at")[:6]

    context = {
        "courses": courses,
    }

    return render(request, "home.html", context)