from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from .models import Course
from .forms import CourseForm, CommentForm
from users.decorators import teacher_required
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import CourseSerializer
from rest_framework import viewsets
from rest_framework import filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from .filters import CourseFilter


def home_view(request):
    if request.user.is_authenticated:
        return redirect('courses:course_list')
    return render(request, 'home.html')


def course_list(request):
    courses = Course.objects.filter(is_published=True).select_related('teacher', 'category')
    return render(request, 'courses/course_list.html', {'courses': courses})



from lessons.models import LessonCompletion


def course_detail(request, slug):
    course = get_object_or_404(
        Course.objects.select_related('teacher', 'category').prefetch_related('lessons', 'comments__author'),
        slug=slug,
        is_published=True
    )

    is_enrolled = False
    is_teacher = False
    completed_lesson_ids = set()
    unlocked_lesson_ids = set()

    all_lessons = list(course.lessons.all().order_by('order', 'id'))

    if request.user.is_authenticated:
        is_teacher = (course.teacher == request.user) or request.user.is_staff
        is_enrolled = course.enrollments.filter(student=request.user).exists()

        if is_teacher:
            unlocked_lesson_ids = set(l.id for l in all_lessons)
        elif is_enrolled:
            completed_lesson_ids = set(
                LessonCompletion.objects.filter(
                    student=request.user,
                    lesson__course=course
                ).values_list('lesson_id', flat=True)
            )
            # Ketma-ket dars ochilish logikasi:
            # 1-dars doim ochiq. Keyingi dars esa oldingi dars yakunlangandagina ochiladi.
            for idx, l in enumerate(all_lessons):
                if idx == 0:
                    unlocked_lesson_ids.add(l.id)
                else:
                    prev_l = all_lessons[idx - 1]
                    if prev_l.id in completed_lesson_ids or l.id in completed_lesson_ids:
                        unlocked_lesson_ids.add(l.id)

    if request.method == 'POST' and request.user.is_authenticated:
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.course = course
            comment.author = request.user
            comment.save()
            messages.success(request, "Izohingiz qo'shildi")
            return redirect('courses:course_detail', slug=slug)
    else:
        comment_form = CommentForm()

    comments = course.comments.all()

    return render(request, 'courses/course_detail.html', {
        'course': course,
        'is_enrolled': is_enrolled,
        'is_teacher': is_teacher,
        'all_lessons': all_lessons,
        'unlocked_lesson_ids': unlocked_lesson_ids,
        'completed_lesson_ids': completed_lesson_ids,
        'comment_form': comment_form,
        'comments': comments,
    })


@login_required
@teacher_required
def course_create(request):
    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.teacher = request.user
            course.save()
            messages.success(request, "Kurs muvaffaqiyatli yaratildi!")
            return redirect('courses:course_list')
    else:
        form = CourseForm()

    return render(request, 'courses/course_form.html', {'form': form, 'is_edit': False})


@login_required
@teacher_required
def course_edit(request, slug):
    """
    Mavjud kursni tahrirlash - rasm, narx, tavsif va h.k. o'zgartirish uchun.
    Faqat kursning O'ZI YARATGAN o'qituvchisi tahrirlay oladi.
    """
    course = get_object_or_404(Course, slug=slug, teacher=request.user)

    if request.method == 'POST':
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, "Kurs muvaffaqiyatli yangilandi!")
            return redirect('courses:teacher_dashboard')
    else:
        form = CourseForm(instance=course)

    return render(request, 'courses/course_form.html', {'form': form, 'is_edit': True, 'course': course})


@login_required
@teacher_required
def teacher_dashboard(request):
    courses = Course.objects.filter(teacher=request.user).annotate(
        student_count=Count('enrollments')
    )
    return render(request, 'courses/teacher_dashboard.html', {'courses': courses})


@login_required
@teacher_required
def course_students(request, slug):
    """
    O'qituvchi uchun kurs talabalari reytingi, foizi va nechanchi darsga kelganligi hisoboti.
    """
    course = get_object_or_404(
        Course.objects.prefetch_related('enrollments__student', 'lessons'),
        slug=slug,
        teacher=request.user
    )

    enrollments = course.enrollments.select_related('student').all()
    all_lessons = list(course.lessons.all().order_by('order', 'id'))
    total_lessons = len(all_lessons)

    completions = LessonCompletion.objects.filter(lesson__course=course).values('student_id', 'lesson_id')
    student_completions = {}
    for comp in completions:
        student_completions.setdefault(comp['student_id'], set()).add(comp['lesson_id'])

    leaderboard = []
    total_progress_sum = 0

    for enrollment in enrollments:
        student_completed_ids = student_completions.get(enrollment.student_id, set())
        completed_count = len(student_completed_ids)

        current_lesson_str = "1-dars (Hali boshlamagan)"
        current_lesson_num = 1
        if total_lessons > 0:
            if completed_count >= total_lessons:
                current_lesson_str = "Barcha darslarni tugatgan 🏆"
                current_lesson_num = total_lessons
            else:
                for idx, les in enumerate(all_lessons):
                    if les.id not in student_completed_ids:
                        current_lesson_num = idx + 1
                        current_lesson_str = f"{idx + 1}-dars: {les.title}"
                        break
        else:
            current_lesson_str = "Darslar yuklanmagan"
            current_lesson_num = 0

        progress = enrollment.progress_percent
        total_progress_sum += progress

        leaderboard.append({
            'student': enrollment.student,
            'enrolled_at': enrollment.enrolled_at,
            'progress_percent': progress,
            'completed_count': completed_count,
            'total_lessons': total_lessons,
            'current_lesson': current_lesson_str,
            'current_lesson_num': current_lesson_num,
            'is_completed': completed_count >= total_lessons and total_lessons > 0,
        })

    # Saralash: Progress foizi yuqori, dars soni ko'p va ertaroq boshlaganlar yuqorida
    leaderboard.sort(key=lambda x: (-x['progress_percent'], -x['completed_count'], x['enrolled_at']))

    for rank, item in enumerate(leaderboard, 1):
        item['rank'] = rank

    total_students_count = len(leaderboard)
    avg_progress = round(total_progress_sum / total_students_count, 1) if total_students_count > 0 else 0
    completed_students_count = sum(1 for item in leaderboard if item['is_completed'])

from enrollments.models import Enrollment


@login_required
@teacher_required
def remove_student(request, slug, student_id):
    """
    O'qituvchi o'z kursidan istalgan talabani chiqarib yuborishi uchun view.
    """
    if request.method == 'POST':
        course = get_object_or_404(Course, slug=slug, teacher=request.user)
        enrollment = get_object_or_404(Enrollment, course=course, student_id=student_id)
        student_name = enrollment.student.username

        # Kursdagi yozilishini va bajargan darslarini o'chirish
        enrollment.delete()
        LessonCompletion.objects.filter(student_id=student_id, lesson__course=course).delete()

        messages.success(request, f"'{student_name}' talabasi '{course.title}' kursidan chiqarib yuborildi.")

    return redirect('courses:course_students', slug=slug)


@login_required
@teacher_required
def course_delete(request, slug):
    """
    Faqat kursning O'ZI YARATGAN o'qituvchisi o'chira oladi -
    get_object_or_404 ichida teacher=request.user filtri shu uchun,
    boshqa o'qituvchi hatto to'g'ri slug bilan ham o'chira olmaydi.
    """
    course = get_object_or_404(Course, slug=slug, teacher=request.user)

    if request.method == 'POST':
        title = course.title
        course.delete()
        messages.success(request, f"'{title}' kursi o'chirildi")
        return redirect('courses:teacher_dashboard')

    return render(request, 'courses/course_confirm_delete.html', {'course': course})


@login_required
@teacher_required
def toggle_publish(request, slug):
    """
    Kursni nashr qilish/qoralamaga qaytarish - bir tugma bosish bilan.
    Faqat POST orqali - GET so'rov (masalan link ustidan sichqoncha
    bilan o'tish, botlar) tasodifan holatni o'zgartirib qo'ymasligi uchun.
    """
    course = get_object_or_404(Course, slug=slug, teacher=request.user)

    if request.method == 'POST':
        course.is_published = not course.is_published
        course.save()

        if course.is_published:
            messages.success(request, f"'{course.title}' nashr qilindi")
        else:
            messages.success(request, f"'{course.title}' qoralamaga qaytarildi")

    return redirect('courses:teacher_dashboard')


from django.db.models import Q
from rest_framework.exceptions import PermissionDenied
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import Course, Category, Comment
from .forms import CourseForm, CommentForm
from users.decorators import teacher_required
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import CourseSerializer, CategorySerializer, CommentSerializer
from rest_framework import viewsets
from rest_framework import filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from .filters import CourseFilter
from .permissions import IsCourseTeacherOrReadOnly


@extend_schema_view(
    list=extend_schema(tags=['Kurslar'], summary='Barcha nashr qilingan kurslar ro\'yxati'),
    retrieve=extend_schema(tags=['Kurslar'], summary='Kurs tafsilotlari'),
    create=extend_schema(tags=['Kurslar'], summary='Yangi kurs yaratish (faqat o\'qituvchilar)'),
    update=extend_schema(tags=['Kurslar'], summary='Kursni to\'liq yangilash'),
    partial_update=extend_schema(tags=['Kurslar'], summary='Kursni qisman yangilash'),
    destroy=extend_schema(tags=['Kurslar'], summary='Kursni o\'chirish'),
)
class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsCourseTeacherOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = CourseFilter
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            if getattr(user, 'role', '') == 'teacher' or user.is_staff:
                return Course.objects.filter(Q(is_published=True) | Q(teacher=user)).select_related('teacher', 'category')
        return Course.objects.filter(is_published=True).select_related('teacher', 'category')

    def perform_create(self, serializer):
        user = self.request.user
        if getattr(user, 'role', '') != 'teacher' and not user.is_staff:
            raise PermissionDenied("Faqat o'qituvchilar kurs yarata oladi.")
        serializer.save(teacher=user)


@extend_schema_view(
    list=extend_schema(tags=['Kategoriyalar'], summary='Barcha kategoriyalar ro\'yxati'),
    retrieve=extend_schema(tags=['Kategoriyalar'], summary='Kategoriya tafsilotlari'),
)
class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = None


@extend_schema_view(
    list=extend_schema(tags=['Izohlar'], summary='Kurs izohlari ro\'yxati'),
    create=extend_schema(tags=['Izohlar'], summary='Kursga izoh qoldirish'),
)
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.select_related('author', 'course').all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['course']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)