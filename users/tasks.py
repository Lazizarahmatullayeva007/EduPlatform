try:
    from celery import shared_task
except ImportError:
    def shared_task(func):
        func.delay = func
        return func

from .eskiz_utils import send_sms


@shared_task
def send_sms_task(phone_number, message):
    """
    SMS xabarini fonda (asinxron) Celery orqali yuborish.
    """
    send_sms(phone_number, message)
