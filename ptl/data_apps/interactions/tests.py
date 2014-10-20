from django.conf import settings
from django.core.management import call_command
from django.test import TestCase

from ..sms.models import Contact
from ..profiles.tests import ConfirmedProfileTestCase
from . import models
from .utils import route_incoming_sms


class ReminderTestCase(ConfirmedProfileTestCase):
    def test_reminders_sent(self):
        """
        Make sure for all circumstances the right number of reminders are sent.
        """
        get_count = Contact.objects.get_num_messages_sent

        # Just the one existing user...
        num_before = get_count()
        call_command('send_reminders')
        self.assertEqual(1, get_count() - num_before)

        # Create another user that's not confirmed.
        num_before = get_count()
        call_command('send_reminders')
        # It shouldn't have sent two reminders, just one (for the confirmed
        # account).
        self.assertEqual(1, get_count() - num_before)


class IncomingSMSRouterTestCase(ConfirmedProfileTestCase):
    def test_route_checkins(self):
        """
        Can we handle an SMS that needs to become a Checkin?
        """
        # TODO: Can this test be more functional - go through Twilio?

        # Test it with each of the following scenarios.
        phone = self.profile.confirmed_contact.phone_number
        num_expected_checkins = 0
        for success, content in ((True, "good"),
                                 (True, "good but I've just been lucky"),
                                 (True, "bad"),
                                 (True, "bad. pray for me dude."),
                                 (True, "ugly :("),
                                 (False, "great"),
                                 (False, "great and good bad ugly")):
            if success:
                num_expected_checkins += 1
            result = route_incoming_sms(phone, content)
            self.assertEqual(success, bool(result),
                             msg="Didn't get {} result for content: {}".
                             format(success, content))

        self.assertEqual(num_expected_checkins, self.profile.checkins.count())

    def test_route_unknown_number(self):
        """
        Do nothing if we get a message from a stranger.
        """
        self.assertEqual(None, route_incoming_sms('+15555550000',
                                                  "bad news mom! car's broken"))
        self.assertEqual(0, models.Checkin.objects.count())

    def test_route_non_checkin_from_profile_number(self):
        """
        Do nothing if we can't discern a checkin from a profile-less user.
        """
        self.assertEqual(None, route_incoming_sms(str(self.profile.confirmed_contact.phone_number),
                                                  "hey there bud"))
        self.assertEqual(0, models.Checkin.objects.count())

    def test_route_checkin_from_non_profile_number(self):
        """
        Do nothing if we get what looks like a checkin from a contact that
        doesn't have a profile.
        """
        self.assertEqual(None, route_incoming_sms('+15555550000',
                                                  "good - let's hang out."))
        self.assertEqual(0, models.Checkin.objects.count())
