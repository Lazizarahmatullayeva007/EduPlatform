from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class ProfileTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='password123',
            role='student'
        )

    def test_profile_view(self):
        self.client.login(username='user1', password='password123')
        response = self.client.get(reverse('users:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'user1@example.com')
        self.assertContains(response, 'Profilni tahrirlash')

    def test_profile_edit(self):
        self.client.login(username='user1', password='password123')
        response = self.client.post(reverse('users:profile'), {
            'bio': 'Software developer from Tashkent',
            'phone_number': '+998901234567'
        }, follow=True)
        self.assertEqual(response.status_code, 200)

        self.user.refresh_from_db()
        self.assertEqual(self.user.bio, 'Software developer from Tashkent')
        self.assertEqual(self.user.phone_number, '+998901234567')

