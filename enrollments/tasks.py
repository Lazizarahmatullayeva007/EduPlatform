try:
    from celery import shared_task
except ImportError:
    def shared_task(func):
        func.delay = func
        return func

from .telegram_utils import send_telegram_message
from django.contrib.auth import get_user_model
from courses.models import Course


@shared_task
def send_telegram_notification_task(text):
    """
    Telegram bildirishnomasini fonda (asinxron) yuborish.
    """
    send_telegram_message(text)


@shared_task
def send_enrollment_email_task(student_id, course_id):
    """
    Talabaga xush kelibsiz emailini fonda (asinxron) yuborish.
    """
    User = get_user_model()
    try:
        student = User.objects.get(pk=student_id)
        course = Course.objects.get(pk=course_id)
        from .email_utils import send_enrollment_email
        send_enrollment_email(student, course)
    except (User.DoesNotExist, Course.DoesNotExist) as e:
        print(f"[CELERY EMAIL XATOSI] {e}")
