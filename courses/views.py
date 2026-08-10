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


class CourseListAPIView(APIView):
    def get(self, request):
        courses = Course.objects.filter(is_published=True)
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.filter(is_published=True)
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = CourseFilter
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'created_at']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)