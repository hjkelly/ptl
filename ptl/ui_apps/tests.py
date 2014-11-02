from urlparse import urlparse

from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase

from . import needles
from ..data_apps.profiles.models import Profile
from ..data_apps.profiles.tests import (
    ProfileTestCase,
    ConfirmedProfileTestCase,
    UnconfirmedProfileTestCase, 
)


class UIMixin(object):
    def assertNeedlesInHaystack(self, needles, haystack):
        """
        Take an iterable of strings to find in the given haystack string.
        """
        for n in needles:
            self.assertIn(n, haystack)

    def assertDestPath(self, resp, url_name):
        """
        This is better than the built in assertRedirects because it's smart
        enough to focus on the path and ignore the query params.
        """
        # Get the URL they're interested in.
        expected_path = reverse(url_name)

        try:
            actual_url = resp.redirect_chain[-1][0]
        # If they weren't redirected, give them useful info.
        except IndexError:
            self.fail("You weren't redirected at all! Got a {} response with "
                      "this content:\n{}".
                      format(resp.status_code, resp.content))

        # Get the path itself, not query params.
        actual_path = urlparse(actual_url).path

        self.assertEqual(expected_path, actual_path)


class AnonymousUserTestCase(UIMixin, ProfileTestCase):
    TEST_NAME = "Fred"
    TEST_EMAIL = "the.test.user@gmail.com"
    TEST_PASSWORD = 'yay!'
    TEST_PHONE = settings.TWILIO_FROM_NUMBER
    REGISTER_DATA = {
        'name': TEST_NAME,
        'email': TEST_EMAIL,
        'phone_number': TEST_PHONE,
    }
    LOGIN_DATA = {
        'username': TEST_EMAIL,
        'password': TEST_PASSWORD,
    }

    def test_can_see_registration_form(self):
        resp = self.client.get(reverse('homepage'))
        self.assertEqual(200, resp.status_code)
        self.assertNeedlesInHaystack(needles.REGISTRATION_FORM, resp.content)

    def test_can_register(self):
        # Submit the form.
        resp = self.client.post(
                reverse('homepage'), self.REGISTER_DATA, follow=True)

        # Did it send us to the dashboard?
        self.assertRedirects(resp, reverse('dashboard'))

        # Make sure a user was created properly.
        self.assertTrue(Profile.objects.get(
                name=self.TEST_NAME, email=self.TEST_EMAIL))

    def test_cannot_register_without_complete_info(self):
        # Leave out each piece of info, one at a time.
        for missing_val in ('name', 'email', 'phone_number'):
            # Form incomplete data.
            incomplete_data = self.REGISTER_DATA.copy()
            incomplete_data.pop(missing_val)
            # Make sure it goes nowhere.
            resp = self.client.post(reverse('homepage'), incomplete_data)
            self.assertContains(resp, '<form', status_code=200)

        # Make sure no users were created.
        self.assertFalse(Profile.objects.count())

    def test_can_see_login_form(self):
        resp = self.client.get(reverse('login'))
        self.assertEqual(200, resp.status_code)
        self.assertNeedlesInHaystack(needles.LOGIN_FORM, resp.content)

    def test_can_login(self):
        # Create a user real quickly.
        self.create_profile(self.TEST_NAME,
                            self.TEST_EMAIL,
                            self.TEST_PASSWORD)

        # Make sure we can log in as that user.
        resp = self.client.post(reverse('login'), self.LOGIN_DATA, follow=True)

        # Were we sent to the dashboard?
        self.assertRedirects(resp, reverse('dashboard'))

    def test_cannot_see_dashboard(self):
        # Try to go there.
        resp = self.client.get(reverse('dashboard'), follow=True)
        # Make sure they were sent to the login page.
        self.assertDestPath(resp, 'login')


class UnconfirmedUserTestCase(UIMixin, UnconfirmedProfileTestCase):
    def test_redirected_from_login(self):
        # Try to go there.
        resp = self.client.get(reverse('login'), follow=True)
        # Make sure they were sent to the dashboard page.
        self.assertRedirects(resp, reverse('dashboard'))

    def test_can_log_out(self):
        # Log them out.
        resp = self.client.get(reverse('logout'))

        # Make sure they can't get to the dashboard now.
        resp = self.client.get(reverse('dashboard'), follow=True)
        # Make sure they were redirected.
        self.assertDestPath(resp, 'login')

    def test_cannot_see_dashboard(self):
        """
        Make sure they see the confirmation instead.
        """
        # Try to go there.
        resp = self.client.get(reverse('dashboard'), follow=True)
        # Make sure they were sent to the login page.
        self.assertRedirects(resp, reverse('confirm'))

    def test_can_see_confirmation_form(self):
        resp = self.client.get(reverse('confirm'))
        self.assertContains(resp, "<form", status_code=200)

    def test_can_confirm(self):
        # Test the correct code, but with superfluous whitespace, and make
        # sure it goes through.
        correct_code = '{} '.format(self.profile.confirmation_code)
        resp = self.client.post(reverse('confirm'), {'code': correct_code}, follow=True)

        # We should end up at the dashboard.
        self.assertRedirects(resp, reverse('dashboard'))

        # Make sure the data was actually changed.
        updated_profile = Profile.objects.get(pk=self.profile.pk)
        self.assertEqual(updated_profile.confirmed_contact,
                         updated_profile.claimed_contact)

    def test_cannot_confirm_without_real_code(self):
        # Test a three-digit confirmation, which is shorter than it should
        # ever be (five digits with a four-digit fallback).
        resp = self.client.post(reverse('confirm'), {'code': '123'})
        self.assertEqual(200, resp.status_code)

        # Make sure the data did not change.
        #updated_profile = Profile.objects.get(pk=self.profile.pk)
        self.assertEqual(None, self.profile.confirmed_contact)


class ConfirmedUserTestCase(UIMixin, ConfirmedProfileTestCase):
    def test_redirected_from_login(self):
        # Try to go there.
        resp = self.client.get(reverse('login'), follow=True)
        # Make sure they were sent to the dashboard page.
        self.assertRedirects(resp, reverse('dashboard'))

    def test_can_log_out(self):
        pass

    def test_can_see_personal_info(self):
        pass

    def test_can_change_personal_info(self):
        pass

    def test_can_see_partners(self):
        pass

    def test_can_add_partners(self):
        pass

    def test_can_remove_partners(self):
        pass
