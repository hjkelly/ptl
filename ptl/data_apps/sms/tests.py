from random import randint

from django.conf import settings
from django.test.utils import override_settings

from ..profiles.tests import CleanTestCase
from . import models


class SMSTests(CleanTestCase):
    def setUp(self):
        super(SMSTests, self).setUp()

    @override_settings(TEST_SENDS_ACTUAL_MESSAGES=True)
    def test_send_and_receive(self):
        """Make sure we can send messages from and to our Twilio number."""
        TEST_BODY = 'testing{}'.format(randint(10000, 99999))
        contact = models.Contact.objects.create(
                phone_number=settings.TWILIO_FROM_NUMBER)

        # Send it and make sure we got an SID from Twilio.
        outgoing_sms = contact.send_sms(TEST_BODY)
        self.assertTrue(outgoing_sms.twilio_sid)

        # Collect incoming messages from the API.
        models.IncomingSMS.objects.fetch_from_twilio()
        models.IncomingSMS.objects.get(body__contains=TEST_BODY)
