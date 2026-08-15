from rest_framework import serializers
from .models import Course, Category, Comment


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']
        read_only_fields = ['id', 'slug']


class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'course', 'author', 'author_name', 'text', 'created_at']
        read_only_fields = ['id', 'author', 'created_at']


class CourseSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.username', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        required=False,
        allow_null=True
    )
    cover_image_url = serializers.SerializerMethodField()
    available_seats = serializers.SerializerMethodField()
    is_full = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'description', 'teacher', 'teacher_name',
            'category', 'category_name', 'price', 'cover_image', 'cover_image_url',
            'max_students', 'available_seats', 'is_full', 'is_published',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'teacher', 'created_at', 'updated_at']

    def get_cover_image_url(self, obj):
        if obj.cover_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.cover_image.url)
            return obj.cover_image.url
        return None

    def get_available_seats(self, obj):
        return obj.available_seats()

    def get_is_full(self, obj):
        return obj.is_full()