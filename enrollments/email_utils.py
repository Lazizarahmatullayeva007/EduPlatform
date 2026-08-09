from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings


def send_enrollment_email(student, course):
    """
    Talaba kursga yozilganda, unga xush kelibsiz emailini yuboradi.
    HTML shablon orqali chiroyli ko'rinishda.
    """
    subject = f"Siz '{course.title}' kursiga yozildingiz!"

    html_message = render_to_string('enrollments/emails/enrollment_confirmation.html', {
        'student': student,
        'course': course,
    })

    send_mail(
        subject=subject,
        message=f"Salom {student.username}, siz {course.title} kursiga muvaffaqiyatli yozildingiz.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[student.email],
        html_message=html_message,
        fail_silently=True,
    )