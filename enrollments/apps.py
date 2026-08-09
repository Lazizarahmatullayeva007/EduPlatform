from django.apps import AppConfig


class EnrollmentsConfig(AppConfig):
    name = 'enrollments'

    def ready(self):
        import enrollments.signals