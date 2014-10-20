from django.test import TestCase

from ...data_apps.profiles.models import Profile
from ...data_apps.profiles.tests import UnconfirmedProfileTestCase


class ConfirmView(UnconfirmedProfileTestCase):
    def test_confirm_view(self):
        """
        Make sure we can confirm this person's account.
        """
        URL = '/dashboard/'

        resp = self.client.get(URL)
        self.assertContains(resp, "<form", status_code=200)

        # Test a three-digit confirmation, which is shorter than it should
        # ever be (five digits with a four-digit fallback).
        resp = self.client.post(URL, {'code': '123'})
        self.assertContains(resp, "<form", status_code=200)

        # Test the correct code, but with superfluous whitespace, and make
        # sure it goes through.
        correct_code = '{} '.format(self.profile.confirmation_code)
        resp = self.client.post(URL, {'code': correct_code})
        # We should be redirected this time.
        self.assertEqual(302, resp.status_code,
                         msg="Instead of redirect, got {}...\n{}".
                         format(resp.status_code, resp.content))

        # Make sure the data was actually changed.
        actual_profile = Profile.objects.get(pk=self.profile.pk)
        self.assertEqual(actual_profile.confirmed_contact,
                         actual_profile.claimed_contact)

        # Make sure we don't get another form.
        resp = self.client.get(URL)
        self.assertNotIn('''name="code"''', resp.content)
