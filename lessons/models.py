from django.db import models
from courses.models import Course


class Lesson(models.Model):
    class LessonType(models.TextChoices):
        VIDEO = 'video', 'Video'
        TEXT = 'text', 'Matn'

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='lessons'
    )
    title = models.CharField(max_length=200)
    lesson_type = models.CharField(
        max_length=10,
        choices=LessonType.choices,
        default=LessonType.VIDEO
    )
    video_url = models.URLField(blank=True, null=True)
    video_file = models.FileField(upload_to='lessons/videos/', blank=True, null=True)
    text_content = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    duration_minutes = models.PositiveIntegerField(default=0, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.video_file:
            try:
                from hachoir.parser import createParser
                from hachoir.metadata import extractMetadata

                parser = createParser(self.video_file.path)
                if parser:
                    metadata = extractMetadata(parser)
                    if metadata and metadata.has('duration'):
                        seconds = metadata.get('duration').total_seconds()
                        minutes = max(1, round(seconds / 60))
                        if minutes != self.duration_minutes:
                            Lesson.objects.filter(pk=self.pk).update(duration_minutes=minutes)
                            self.duration_minutes = minutes
            except Exception:
                pass


@property
def embed_video_url(self):
    if not self.video_url:
        return ''
        url = self.video_url
    if 'youtu.be/' in url:
        video_id = url.split('youtu.be/')[-1].split('?')[0]
        return f'https://www.youtube.com/embed/{video_id}'
    if 'watch?v=' in url:
        video_id = url.split('watch?v=')[-1].split('&')[0]
        return f'https://www.youtube.com/embed/{video_id}'
    return url
