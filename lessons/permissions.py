from rest_framework import permissions


class IsLessonTeacherOrReadOnly(permissions.BasePermission):
    """
    Darsni faqat shu kursning o'qituvchisi yarata, tahrirlay yoki o'chira oladi.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.course.teacher == request.user or request.user.is_staff
