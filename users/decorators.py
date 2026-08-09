from django.core.exceptions import PermissionDenied
from functools import wraps


def teacher_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'teacher':
            raise PermissionDenied("Faqat o'qituvchilar uchun.")
        return view_func(request, *args, **kwargs)
    return wrapper