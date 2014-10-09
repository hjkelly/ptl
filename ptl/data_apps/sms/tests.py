from django.conf import settings

from ...test import CleanTestCase
from .models import Contact


class SmsTests(CleanTestCase):
    def test_send_sms_and_get_sms(self):
        TEST_BODY = "blah"

        # Send it!
        c = Contact(phone_number=settings.TEST_PHONE_NUMBER)
        c.send_sms(TEST_BODY)

        # Hit up the API to make sure it was sent.
        last_sms = c.get_last_sms()
        self.assertNotEqual(last_sms, None)
        self.assertEqual(last_sms.body, TEST_BODY)
