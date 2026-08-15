from rest_framework import serializers
from .models import Lesson, LessonCompletion


class LessonSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    embed_video_url = serializers.CharField(read_only=True)
    video_file_url = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = [
            'id', 'course', 'course_title', 'title', 'lesson_type',
            'video_url', 'video_file', 'video_file_url', 'embed_video_url',
            'text_content', 'order', 'duration_minutes', 'created_at',
        ]
        read_only_fields = ['id', 'created_at', 'duration_minutes']

    def get_video_file_url(self, obj):
        if obj.video_file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.video_file.url)
            return obj.video_file.url
        return None


class LessonCompletionSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source='lesson.title', read_only=True)

    class Meta:
        model = LessonCompletion
        fields = ['id', 'student', 'lesson', 'lesson_title', 'completed_at']
        read_only_fields = ['id', 'student', 'completed_at']