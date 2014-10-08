from django.core.exceptions import ValidationError

from ...test import CleanTestCase
from .models import Profile


class ProfileTests(CleanTestCase):
    def test_create(self):
        Profile.objects.create('a@gmail.com', 'testpass', '9876543210')
        self.assertEqual(1, Profile.objects.count())
