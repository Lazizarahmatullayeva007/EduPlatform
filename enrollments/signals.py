import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Enrollment
from .tasks import send_telegram_notification_task, send_enrollment_email_task

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Enrollment)
def notify_teacher_on_enrollment(sender, instance, created, **kwargs):
    """
    Yangi Enrollment yaratilganda (kursga yozilganda), o'qituvchiga
    Telegram orqali xabar va talabaga emailni asinxron (Celery orqali) yuboradi.
    Agar Celery/Redis ishlamayotgan bo'lsa, xatolik yuz bermasdan
    to'g'ridan-to'g'ri (fallback) yuboriladi.
    """
    if not created:
        return

    text = (
        f"Yangi talaba yozildi!\n"
        f"Kurs: {instance.course.title}\n"
        f"Talaba: {instance.student.username}"
    )

    try:
        send_telegram_notification_task.delay(text)
    except Exception as e:
        logger.warning(f"Telegram bildirishnoma yuborishda xatolik (Celery): {e}")
        try:
            from .telegram_utils import send_telegram_message
            send_telegram_message(text)
        except Exception as direct_err:
            logger.error(f"Telegram bevosita yuborishda xatolik: {direct_err}")

    try:
        send_enrollment_email_task.delay(instance.student_id, instance.course_id)
    except Exception as e:
        logger.warning(f"Email bildirishnoma yuborishda xatolik (Celery): {e}")
        try:
            from .email_utils import send_enrollment_email
            send_enrollment_email(instance.student, instance.course)
        except Exception as direct_err:
            logger.error(f"Email bevosita yuborishda xatolik: {direct_err}")