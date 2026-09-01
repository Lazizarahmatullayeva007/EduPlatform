from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Enrollment
from .tasks import send_telegram_notification_task, send_enrollment_email_task


@receiver(post_save, sender=Enrollment)
def notify_teacher_on_enrollment(sender, instance, created, **kwargs):
    """
    Yangi Enrollment yaratilganda (kursga yozilganda), o'qituvchiga
    Telegram orqali xabar va talabaga emailni asinxron (Celery orqali) yuboradi.
    """
    if not created:
        return

    text = (
        f"Yangi talaba yozildi!\n"
        f"Kurs: {instance.course.title}\n"
        f"Talaba: {instance.student.username}"
    )
    # Celery orqali fonda bajarish
    send_telegram_notification_task.delay(text)
    send_enrollment_email_task.delay(instance.student_id, instance.course_id)