from django.contrib.auth.models import User
from django.test import TestCase

from .data_apps.sms.models import Contact
from .data_apps.profiles.models import Profile


class CleanTestCase(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        Profile.objects.all().delete()
        User.objects.all().delete()
        Contact.objects.all().delete()
