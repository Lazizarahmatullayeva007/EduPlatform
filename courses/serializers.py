from rest_framework import serializers
from .models import Course


class CourseSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    available_seats = serializers.SerializerMethodField()
    is_full = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'description', 'teacher_name', 'category_name',
            'price', 'max_students', 'available_seats', 'is_full', 'is_published',
        ]

    def get_available_seats(self, obj):
        return obj.available_seats()

    def get_is_full(self, obj):
        return obj.is_full()