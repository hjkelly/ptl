from django.conf import settings
from django.contrib.auth.models import User
from django.test import SimpleTestCase

from ...data_apps.sms.models import Contact, OutgoingSMS
from .models import Partnership, Profile


class CleanTestCase(SimpleTestCase):
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
    def test_create(self):
        # Create a new profile!
        p = Profile.objects.create(name="Frank", email="frank@test.com",
                                   password="testpass",
                                   phone_number=settings.TWILIO_FROM_NUMBER)

        # Make sure it's in the DB.
        self.assertTrue(isinstance(p.pk, (int, long)))
        # Make sure we sent a confirmation message.
        self.assertTrue(1, p.claimed_contact.outgoing_smses.count())
        # Make sure the confirmation code isn't the default.
        self.assertNotEqual(p.confirmation_code,
                            Profile.DEFAULT_CONFIRMATION_CODE)

    def get_another_test_profile_without_confirmation(self, phone_number):
        outgoing_count_before = OutgoingSMS.objects.count()

        c = Contact.objects.create(phone_number=phone_number)
        FAKE_VAL = "test_str@test.com"
        # Provide the contact as the confirmed one as well; this should avoid
        # the SMS.
        p = Profile.objects.create(name=FAKE_VAL,
                                   email=FAKE_VAL,
                                   password=FAKE_VAL,
                                   claimed_contact=c,
                                   confirmed_contact=c)

        # Make sure no messages were sent.
        self.assertEqual(outgoing_count_before, OutgoingSMS.objects.count())

        return p


class UnconfirmedProfileTestCase(ProfileTestCase):
    """
    Provide a registered but unconfirmed user, and log the test client in.
    """
    NAME = "Freddy"
    EMAIL = 'test_user@mydomain.com'
    PASSWORD = 'lkaj3k3jv!'

    def setUp(self):
        super(UnconfirmedProfileTestCase, self).setUp()
        # Attach a profile.
        self.profile = Profile.objects.create(
                name=self.NAME,
                email=self.EMAIL,
                password=self.PASSWORD,
                phone_number=settings.TWILIO_FROM_NUMBER)
        # Log the test client in.
        self.assertTrue(self.client.login(username=self.EMAIL,
                                          password=self.PASSWORD))


class ConfirmedProfileTestCase(UnconfirmedProfileTestCase):
    def setUp(self):
        super(ConfirmedProfileTestCase, self).setUp()
        # Confirm on this end.
        self.profile.confirmed_contact = self.profile.claimed_contact
        self.profile.save()


class PartnershipTestCase(ConfirmedProfileTestCase):
    PARTNER_NUMBERS = (
        '+19195551234',
        '+19195555678',
    )

    def test_partner_creation(self):
        """
        Upon creation, do they have a confirmation string and receive an SMS?
        """
        p = Partnership.objects.create(
                profile=self.profile,
                name="Bobby",
                phone_number=self.PARTNER_NUMBERS[0])
        # Make sure its status works out properly.
        self.assertEqual(str(p.contact.phone_number), self.PARTNER_NUMBERS[0])
        self.assertEqual(p.confirmed, False)
        self.assertEqual(p.confirmation_string,
                         settings.TWILIO_FROM_NUMBER[-4:])

    def test_partner_recovers_from_duplicate_confirmation_string(self):
        """
        It should try to recover from ambiguous confirmation strings.
        """
        other_profile = self.get_another_test_profile_without_confirmation(
                '+1919456'+settings.TWILIO_FROM_NUMBER[-4:])
        # Create a partner for both profiles.
        partner_1 = Partnership.objects.create(profile=self.profile, name="Jim",
                                               phone_number=self.PARTNER_NUMBERS[0])
        partner_2 = Partnership.objects.create(profile=other_profile, name="Jim",
                                               phone_number=self.PARTNER_NUMBERS[0])
        self.assertNotEqual(partner_1.confirmation_string,
                            partner_2.confirmation_string)

    def test_profile_can_get_confirmed_partners(self):
        p = Partnership.objects.create(
                profile=self.profile,
                name="Bobby",
                phone_number=self.PARTNER_NUMBERS[0],
                confirmed=True)
        self.assertEqual(1, len(self.profile.get_confirmed_partners()))
