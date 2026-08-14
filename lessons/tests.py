from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from courses.models import Course, Category
from lessons.models import Lesson, LessonCompletion
from enrollments.models import Enrollment

User = get_user_model()


class LessonProgressTests(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='teacher1',
            email='teacher@example.com',
            password='password123',
            role='teacher'
        )
        self.student = User.objects.create_user(
            username='student1',
            email='student@example.com',
            password='password123',
            role='student'
        )
        self.category = Category.objects.create(name='IT', slug='it')
        self.course = Course.objects.create(
            title='Python Core',
            slug='python-core',
            description='Python course',
            teacher=self.teacher,
            category=self.category,
            is_published=True
        )
        self.lesson1 = Lesson.objects.create(
            course=self.course,
            title='Lesson 1: Intro',
            order=1
        )
        self.lesson2 = Lesson.objects.create(
            course=self.course,
            title='Lesson 2: Variables',
            order=2
        )
        self.enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course
        )

    def test_complete_lesson_updates_progress_percent(self):
        self.client.login(username='student1', password='password123')

        url1 = reverse('lessons:complete_lesson', kwargs={'course_slug': self.course.slug, 'lesson_id': self.lesson1.id})
        response1 = self.client.post(url1, follow=True)

        self.assertEqual(response1.status_code, 200)
        self.assertTrue(LessonCompletion.objects.filter(student=self.student, lesson=self.lesson1).exists())

        self.enrollment.refresh_from_db()
        self.assertEqual(self.enrollment.progress_percent, 50)

        # Complete second lesson
        url2 = reverse('lessons:complete_lesson', kwargs={'course_slug': self.course.slug, 'lesson_id': self.lesson2.id})
        response2 = self.client.post(url2, follow=True)

        self.assertEqual(response2.status_code, 200)
        self.enrollment.refresh_from_db()
        self.assertEqual(self.enrollment.progress_percent, 100)

