from rest_framework.permissions import BasePermission
from courses.models import Course


class CourseNotFull(BasePermission):
    """
    Faqat POST (yangi yozilish) so'rovlari uchun tekshiradi:
    agar kursda bo'sh o'rin qolmagan bo'lsa, ruxsat bermaydi.
    Boshqa metodlar (GET, DELETE va h.k.) uchun har doim ruxsat beradi.
    """
    message = "Bu kursda bo'sh o'rin qolmagan."

    def has_permission(self, request, view):
        if request.method != 'POST':
            return True

        course_id = request.data.get('course')
        if not course_id:
            return True

        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return True

        return not course.is_full()