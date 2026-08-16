from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework import viewsets, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from courses.models import Course
from enrollments.models import Enrollment
from users.decorators import teacher_required
from .models import Lesson, LessonCompletion
from .serializers import LessonSerializer
from .forms import LessonForm


@login_required
def lesson_detail(request, course_slug, lesson_id):
    """
    Dars tafsiloti sahifasi.
    1. Faqat SHU KURSGA YOZILGAN (to'lov qilgan) talaba yoki kurs o'qituvchisi ko'ra oladi.
    2. Ketma-ket ochilish qoidasi: 1-dars ochiq, keyingi har bir dars oldingisi yakunlangandagina ochiladi.
    """
    lesson = get_object_or_404(Lesson, id=lesson_id, course__slug=course_slug)
    course = lesson.course

    is_enrolled = course.enrollments.filter(student=request.user).exists()
    is_teacher = (course.teacher == request.user) or request.user.is_staff

    if not (is_enrolled or is_teacher):
        messages.error(request, "Darslarni ko'rish uchun avval ushbu kursga yoziling yoki to'lovni amalga oshiring.")
        return render(request, 'lessons/lesson_forbidden.html', {'course': course}, status=403)

    all_lessons = list(course.lessons.all().order_by('order', 'id'))
    completed_lesson_ids = set(
        LessonCompletion.objects.filter(
            student=request.user,
            lesson__course=course
        ).values_list('lesson_id', flat=True)
    )

    unlocked_lesson_ids = set()
    if is_teacher:
        unlocked_lesson_ids = set(l.id for l in all_lessons)
    else:
        for idx, l in enumerate(all_lessons):
            if idx == 0:
                unlocked_lesson_ids.add(l.id)
            else:
                prev_l = all_lessons[idx - 1]
                if prev_l.id in completed_lesson_ids or l.id in completed_lesson_ids:
                    unlocked_lesson_ids.add(l.id)

    # Qulflangan darsga URL orqali to'g'ridan-to'g'ri kirishga urinsa bloklaymiz
    if lesson.id not in unlocked_lesson_ids:
        messages.warning(request, "🔒 Ushbu dars qulflangan! Avval oldingi darsni yakunlashingiz kerak.")
        return redirect('courses:course_detail', slug=course.slug)

    is_completed = lesson.id in completed_lesson_ids

    # Keyingi darsni aniqlash
    next_lesson = None
    prev_lesson = None
    for idx, l in enumerate(all_lessons):
        if l.id == lesson.id:
            if idx + 1 < len(all_lessons):
                next_lesson = all_lessons[idx + 1]
            if idx > 0:
                prev_lesson = all_lessons[idx - 1]
            break

    return render(request, 'lessons/lesson_detail.html', {
        'lesson': lesson,
        'course': course,
        'all_lessons': all_lessons,
        'is_completed': is_completed,
        'completed_lesson_ids': completed_lesson_ids,
        'unlocked_lesson_ids': unlocked_lesson_ids,
        'next_lesson': next_lesson,
        'prev_lesson': prev_lesson,
    })


@login_required
def complete_lesson(request, course_slug, lesson_id):
    """
    Darsni muvaffaqiyatli yakunlash, progress_percent'ni yangilash
    va keyingi darsni avtomatik ochish.
    """
    if request.method == 'POST':
        lesson = get_object_or_404(Lesson, id=lesson_id, course__slug=course_slug)
        course = lesson.course

        enrollment = Enrollment.objects.filter(student=request.user, course=course).first()
        is_teacher = (course.teacher == request.user) or request.user.is_staff

        if not (enrollment or is_teacher):
            return render(request, 'lessons/lesson_forbidden.html', {'course': course}, status=403)

        LessonCompletion.objects.get_or_create(
            student=request.user,
            lesson=lesson
        )

        all_lessons = list(course.lessons.all().order_by('order', 'id'))
        next_lesson = None
        for idx, l in enumerate(all_lessons):
            if l.id == lesson.id and idx + 1 < len(all_lessons):
                next_lesson = all_lessons[idx + 1]
                break

        if enrollment:
            total_lessons = len(all_lessons)
            completed_count = LessonCompletion.objects.filter(
                student=request.user,
                lesson__course=course
            ).count()

            progress = int((completed_count / total_lessons) * 100) if total_lessons > 0 else 100
            if progress > 100:
                progress = 100

            enrollment.progress_percent = progress
            enrollment.save()

        if next_lesson:
            messages.success(request, f"🎉 '{lesson.title}' darsini yakunladingiz! Keyingi dars ochildi.")
            return redirect('lessons:lesson_detail', course_slug=course_slug, lesson_id=next_lesson.id)
        else:
            messages.success(request, "🏆 Tabriklaymiz! Siz ushbu kursdagi barcha darslarni to'liq yakunladingiz!")
            return redirect('courses:course_detail', slug=course_slug)

    return redirect('lessons:lesson_detail', course_slug=course_slug, lesson_id=lesson_id)


@login_required
@teacher_required
def lesson_create(request, course_slug):
    """
    Faqat kursning O'ZI YARATGAN o'qituvchisi dars qo'sha oladi.
    """
    course = get_object_or_404(Course, slug=course_slug, teacher=request.user)

    if request.method == 'POST':
        form = LessonForm(request.POST, request.FILES)
        if form.is_valid():
            lesson = form.save(commit=False)
            lesson.course = course
            lesson.save()
            messages.success(request, f"'{lesson.title}' darsi qo'shildi")
            return redirect('courses:course_detail', slug=course.slug)
    else:
        form = LessonForm()

    return render(request, 'lessons/lesson_form.html', {'form': form, 'course': course})


@login_required
@teacher_required
def lesson_delete(request, course_slug, lesson_id):
    """
    Faqat kursning O'ZI YARATGAN o'qituvchisi darsni o'chira oladi.
    """
    lesson = get_object_or_404(Lesson, id=lesson_id, course__slug=course_slug, course__teacher=request.user)

    if request.method == 'POST':
        title = lesson.title
        course_slug_val = lesson.course.slug
        lesson.delete()
        messages.success(request, f"'{title}' darsi o'chirildi")
        return redirect('courses:course_detail', slug=course_slug_val)

    return render(request, 'lessons/lesson_confirm_delete.html', {'lesson': lesson})


from django.db.models import Q
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, extend_schema_view
from .permissions import IsLessonTeacherOrReadOnly


@extend_schema_view(
    list=extend_schema(tags=['Darslar'], summary='Darslar ro\'yxati'),
    retrieve=extend_schema(tags=['Darslar'], summary='Dars tafsilotlari'),
    create=extend_schema(tags=['Darslar'], summary='Kursga yangi dars qo\'shish (faqat o\'qituvchi)'),
    update=extend_schema(tags=['Darslar'], summary='Darsni to\'liq yangilash'),
    partial_update=extend_schema(tags=['Darslar'], summary='Darsni qisman yangilash'),
    destroy=extend_schema(tags=['Darslar'], summary='Darsni o\'chirish'),
)
class LessonViewSet(viewsets.ModelViewSet):
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsLessonTeacherOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['course', 'lesson_type']
    search_fields = ['title', 'text_content']
    ordering_fields = ['order', 'duration_minutes', 'created_at']
    ordering = ['order']

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            if getattr(user, 'role', '') == 'teacher' or user.is_staff:
                return Lesson.objects.filter(
                    Q(course__is_published=True) | Q(course__teacher=user)
                ).select_related('course')
        return Lesson.objects.filter(course__is_published=True).select_related('course')

    def retrieve(self, request, *args, **kwargs):
        lesson = self.get_object()
        course = lesson.course
        user = request.user

        if not user.is_authenticated:
            return Response({"detail": "Dars materialini ko'rish uchun tizimga kiring va kursga yoziling."}, status=401)

        is_teacher = (course.teacher == user) or user.is_staff
        is_enrolled = course.enrollments.filter(student=user).exists()

        if not (is_teacher or is_enrolled):
            return Response({"detail": "Ushbu darsni ko'rish uchun kursga to'lov qilishingiz yoki yozilishingiz kerak."}, status=403)

        # Ketma-ket dars ochilishini tekshirish
        if not is_teacher:
            all_lessons = list(course.lessons.all().order_by('order', 'id'))
            completed_ids = set(
                LessonCompletion.objects.filter(student=user, lesson__course=course).values_list('lesson_id', flat=True)
            )
            unlocked_ids = set()
            for idx, l in enumerate(all_lessons):
                if idx == 0:
                    unlocked_ids.add(l.id)
                else:
                    prev_l = all_lessons[idx - 1]
                    if prev_l.id in completed_ids or l.id in completed_ids:
                        unlocked_ids.add(l.id)

            if lesson.id not in unlocked_ids:
                return Response({"detail": "Ushbu dars qulflangan. Oldingi darsni yakunlang."}, status=403)

        serializer = self.get_serializer(lesson)
        return Response(serializer.data)

    def perform_create(self, serializer):
        course = serializer.validated_data.get('course')
        if course.teacher != self.request.user and not self.request.user.is_staff:
            raise PermissionDenied("Faqat kurs muallifi ushbu kursga dars qo'sha oladi.")
        serializer.save()

    @extend_schema(
        tags=['Darslar'],
        summary='Darsni yakunlash (Talaba uchun)',
        responses={200: {"type": "object", "properties": {"message": {"type": "string"}, "progress": {"type": "integer"}}}}
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticatedOrReadOnly])
    def complete(self, request, pk=None):
        if not request.user.is_authenticated:
            return Response({"error": "Avval tizimga kiring"}, status=401)
        lesson = self.get_object()
        course = lesson.course

        enrollment = Enrollment.objects.filter(student=request.user, course=course).first()
        is_teacher = (course.teacher == request.user) or request.user.is_staff

        if not (enrollment or is_teacher):
            return Response({"error": "Siz ushbu kursga yozilmagansiz"}, status=403)

        LessonCompletion.objects.get_or_create(student=request.user, lesson=lesson)

        progress = 0
        if enrollment:
            total_lessons = course.lessons.count()
            completed_count = LessonCompletion.objects.filter(
                student=request.user,
                lesson__course=course
            ).count()
            progress = int((completed_count / total_lessons) * 100) if total_lessons > 0 else 100
            progress = min(100, progress)
            enrollment.progress_percent = progress
            enrollment.save()

        return Response({"message": "Dars muvaffaqiyatli yakunlandi", "progress": progress})
