from django.db import models
from django.conf import settings
from courses.models import Course
import uuid


class Enrollment(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)
    progress_percent = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.username} → {self.course.title}"


class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Kutilmoqda'),
        ('paid', 'To\'landi'),
        ('cancelled', 'Bekor qilindi'),
    ]

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='payments'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=64, unique=True, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.student.username} — {self.course.title} — {self.status}"