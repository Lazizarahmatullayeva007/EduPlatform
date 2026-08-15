from rest_framework import permissions


class IsCourseTeacherOrReadOnly(permissions.BasePermission):
    """
    Kursni faqat uni yaratgan o'qituvchi o'zgartira yoki o'chira oladi.
    Boshqalar faqat o'qishi (GET, HEAD, OPTIONS) mumkin.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.teacher == request.user or request.user.is_staff
