from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Enrollment
from .telegram_utils import send_telegram_message


@receiver(post_save, sender=Enrollment)
def notify_teacher_on_enrollment(sender, instance, created, **kwargs):
    """
    Yangi Enrollment yaratilganda (kursga yozilganda), o'qituvchiga
    Telegram orqali xabar yuboradi. Faqat YANGI yaratilganda ishlaydi
    (mavjud Enrollment yangilanganda emas).
    """
    if not created:
        return

    text = (
        f"Yangi talaba yozildi!\n"
        f"Kurs: {instance.course.title}\n"
        f"Talaba: {instance.student.username}"
    )
    send_telegram_message(text)

    from .email_utils import send_enrollment_email
    send_enrollment_email(instance.student, instance.course)