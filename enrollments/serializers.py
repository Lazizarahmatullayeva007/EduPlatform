from rest_framework import serializers
from .models import Enrollment, Payment
from courses.models import Course


class EnrollmentSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    course_slug = serializers.CharField(source='course.slug', read_only=True)
    course_cover = serializers.SerializerMethodField()

    class Meta:
        model = Enrollment
        fields = ['id', 'course', 'course_title', 'course_slug', 'course_cover', 'enrolled_at', 'progress_percent']
        read_only_fields = ['id', 'enrolled_at']

    def get_course_cover(self, obj):
        if obj.course.cover_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.course.cover_image.url)
            return obj.course.cover_image.url
        return None

    def validate(self, attrs):
        user = self.context['request'].user
        course = attrs.get('course')
        if not course:
            raise serializers.ValidationError({"course": "Kurs ko'rsatilishi shart."})

        if Enrollment.objects.filter(student=user, course=course).exists():
            raise serializers.ValidationError({"course": "Siz allaqachon bu kursga yozilgansiz."})

        if course.is_full():
            raise serializers.ValidationError({"course": "Bu kursda bo'sh o'rin qolmagan."})

        return attrs


class PaymentSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    student_username = serializers.CharField(source='student.username', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'student', 'student_username', 'course', 'course_title',
            'amount', 'status', 'transaction_id', 'created_at', 'paid_at'
        ]
        read_only_fields = ['id', 'student', 'status', 'transaction_id', 'created_at', 'paid_at']


class InitiatePaymentResponseSerializer(serializers.Serializer):
    transaction_id = serializers.CharField()
    amount = serializers.CharField()
    message = serializers.CharField()