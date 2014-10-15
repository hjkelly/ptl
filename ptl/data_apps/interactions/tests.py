from django.core.management import call_command
from django.test import TestCase

from ..sms.models import Contact
from ..profiles.tests import ConfirmedProfileTestCase


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
        p2 = self.create_profile('a', 'a@b.com', 'pass')
        # It shouldn't send a second reminder yet (they're not confirmed).
        num_before = get_count()
        call_command('send_reminders')
        self.assertEqual(1, get_count() - num_before)

        # Confirm that user.
        p2.confirmed = True
        p2.save()
        # Now it should send two reminders.
        num_before = get_count()
        call_command('send_reminders')
        self.assertEqual(2, get_count() - num_before)
