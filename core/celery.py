import os
from celery import Celery

# Django settings modulini ko'rsatish
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')

# Celery sozlamalarini settings.py dan CELERY_ prefiksi bilan o'qish
app.config_from_object('django.conf:settings', namespace='CELERY')

# Barcha o'rnatilgan ilovalardagi tasks.py fayllarini avtomatik topish
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
