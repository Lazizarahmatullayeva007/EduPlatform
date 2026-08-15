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



def course_detail(request, slug):
    course = get_object_or_404(
        Course.objects.select_related('teacher', 'category').prefetch_related('lessons', 'comments__author'),
        slug=slug,
        is_published=True
    )

    is_enrolled = False
    if request.user.is_authenticated:
        is_enrolled = course.enrollments.filter(student=request.user).exists()

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