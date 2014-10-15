from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase

from ...data_apps.sms.models import Contact
from ...data_apps.profiles.models import Profile
from .models import Profile


class CleanTestCase(TestCase):
    """
    Make sure data is wiped after each test case.
    """
    def setUp(self):
        """
        Wipe all the things!
        """
        User.objects.all().delete()
        Contact.objects.all().delete()

    def tearDown(self):
        pass


class ProfileTestCase(CleanTestCase):
    def create_profile(self, name, email, passwd):
        return Profile.objects.create(name, email, passwd,
                                      settings.TEST_PHONE_NUMBER)

    def test_create(self):
        # Create a new profile!
        p = self.create_profile('Fred', 'a@gmail.com', 'testpass')

        # Make sure it's in the DB.
        self.assertTrue(isinstance(p.pk, (int, long)))
        # Make sure we sent a confirmation message.
        self.assertTrue(p.contact.last_sid)
        # Make sure the confirmation code isn't the default.
        self.assertNotEqual(p.confirmation_code,
                            Profile.DEFAULT_CONFIRMATION_CODE)


class UnconfirmedProfileTestCase(ProfileTestCase):
    """
    Provide a registered but unconfirmed user, and log the test client in.
    """
    USERNAME = EMAIL = 'test_user@mydomain.com'
    PASSWORD = 'lkaj3k3jv!'

    def setUp(self):
        super(UnconfirmedProfileTestCase, self).setUp()
        # Attach a profile.
        self.profile = Profile.objects.create(
                self.USERNAME,
                self.EMAIL,
                self.PASSWORD,
                settings.TEST_PHONE_NUMBER)
        # Log the test client in.
        self.assertTrue(self.client.login(username=self.USERNAME,
                                          password=self.PASSWORD))


class ConfirmedProfileTestCase(UnconfirmedProfileTestCase):
    def setUp(self):
        super(ConfirmedProfileTestCase, self).setUp()
        # Attach a profile.
        self.profile.confirmed = True
        self.profile.save()
