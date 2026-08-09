from django.contrib import admin
from .models import Lesson


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'lesson_type', 'order', 'duration_minutes']
    list_filter = ['lesson_type', 'course']
    search_fields = ['title']
    ordering = ['course', 'order']