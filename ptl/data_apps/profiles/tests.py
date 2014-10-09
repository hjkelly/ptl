from django.conf import settings
from django.core.exceptions import ValidationError

from ...test import CleanTestCase
from .models import Profile


class ProfileTests(CleanTestCase):
    def test_create(self):
        # Create a new profile!
        p = Profile.objects.create('Fred', 'a@gmail.com', 'testpass',
                                   settings.TEST_PHONE_NUMBER)

        # Make sure it's in the DB.
        self.assertTrue(isinstance(p.pk, (int, long)))
        # Make sure we sent a confirmation message.
        self.assertTrue(p.contact.last_sid)
        # Make sure the confirmation code isn't the default.
        self.assertNotEqual(p.confirmation_code,
                            Profile.DEFAULT_CONFIRMATION_CODE)
