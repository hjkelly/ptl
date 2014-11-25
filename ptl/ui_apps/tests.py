from urlparse import urlparse

from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase

from . import needles
from ..data_apps.profiles.models import Profile, Partnership
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

    def get_last_redirect_destination(self, resp):
        if getattr(resp, 'redirect_chain', []):
            try:
                actual_url = resp.redirect_chain[-1][0]
            # If they weren't redirected, give them useful info.
            except IndexError:
                self.fail("You weren't redirected at all! Got a {} response with "
                          "this content:\n{}".
                          format(resp.status_code, resp.content))
        else:
            actual_url = resp['Location']

        # Get the path itself, not query params.
        return urlparse(actual_url).path

    def assertRespStatusIs(self, resp, acceptable_status_codes):
        """
        If the status code doesn't match, try to give more info.
        """

        # Force an int to a tuple!
        if isinstance(acceptable_status_codes, int):
            acceptable_status_codes = (acceptable_status_codes,)

        # If the response isn't one of the options...
        if resp.status_code not in acceptable_status_codes:
            # If it was a redirect, where to?
            if resp.status_code in (301, 302):
                self.fail("Instead of {}, got a redirect to: {}".
                          format(acceptable_status_codes,
                                 self.get_last_redirect_destination(resp)))
            # Otherwise, what was the content?
            else:
                self.fail("Instead of {}, got a {} with content:\n{}".
                          format(acceptable_status_codes,
                                 resp.status_code,
                                 resp.content))

    def assertIsRedirect(self, resp):
        self.assertTrue(
                resp.redirect_chain or resp.get('Location', False),
                msg="The response wasn't a redirect, but a {}:\n{}".
                format(resp.status_code, resp.content))

    def assertDestPath(self, resp, url_name):
        """
        This is better than the built in assertRedirects because it's smart
        enough to focus on the path and ignore the query params.
        """
        # Make sure we're dealing with a redirect.
        self.assertIsRedirect(resp)

        # Make sure the URL they hoped for matches where we landed.
        self.assertEqual(reverse(url_name),
                         self.get_last_redirect_destination(resp))


class AnonymousUserTestCase(UIMixin, ProfileTestCase):
    TEST_NAME = "Fred"
    TEST_EMAIL = "the.test.user@gmail.com"
    TEST_PASSWORD = 'yay!'
    TEST_PHONE = settings.TWILIO_FROM_NUMBER
    REGISTER_DATA = {
        'name': TEST_NAME,
        'email': TEST_EMAIL,
        'password': TEST_PASSWORD,
        'phone_number': TEST_PHONE,
    }
    LOGIN_DATA = {
        'username': TEST_EMAIL,
        'password': TEST_PASSWORD,
    }

    def test_can_see_registration_form(self):
        resp = self.client.get(reverse('homepage'))
        self.assertRespStatusIs(resp, 200)
        self.assertNeedlesInHaystack(needles.REGISTRATION_FORM, resp.content)
        self.assertNeedlesInHaystack(needles.ANONYMOUS_CONTROLS, resp.content)

    def test_can_register(self):
        # Submit the form.
        resp = self.client.post(
                reverse('homepage'), self.REGISTER_DATA, follow=True)

        # Did it send us to the dashboard?
        self.assertDestPath(resp, 'confirm')

        # Make sure a user was created properly.
        self.assertTrue(Profile.objects.get(name=self.TEST_NAME,
                                            user__username=self.TEST_EMAIL,
                                            user__email=self.TEST_EMAIL),
                        msg="The new user wasn't found in the DB.")

    def test_cannot_register_without_complete_info(self):
        # Leave out each piece of info, one at a time.
        for missing_val in self.REGISTER_DATA.keys():
            # Form incomplete data.
            incomplete_data = self.REGISTER_DATA.copy()
            incomplete_data.pop(missing_val)
            # Make sure it goes nowhere.
            resp = self.client.post(reverse('homepage'), incomplete_data)
            self.assertRespStatusIs(resp, 200)
            self.assertNeedlesInHaystack(needles.REGISTRATION_FORM,
                                         resp.content)
            self.assertNeedlesInHaystack(needles.ANONYMOUS_CONTROLS,
                                         resp.content)

        # Make sure no users were created.
        self.assertFalse(Profile.objects.count())

    def test_can_see_login_form(self):
        resp = self.client.get(reverse('login'))
        self.assertRespStatusIs(resp, 200)
        self.assertNeedlesInHaystack(needles.LOGIN_FORM, resp.content)
        self.assertNeedlesInHaystack(needles.ANONYMOUS_CONTROLS, resp.content)

    def test_can_login(self):
        # Create a user real quickly.
        Profile.objects.create(name=self.TEST_NAME,
                               email=self.TEST_EMAIL,
                               password=self.TEST_PASSWORD,
                               phone_number=settings.TWILIO_FROM_NUMBER)

        # Make sure we can log in as that user.
        resp = self.client.post(reverse('login'), self.LOGIN_DATA, follow=True)

        # Were we sent to the dashboard?
        self.assertDestPath(resp, 'confirm')

    def test_cannot_see_dashboard(self):
        # Try to go there.
        resp = self.client.get(reverse('dashboard'), follow=True)
        # Make sure they were sent to the login page.
        self.assertDestPath(resp, 'login')
        self.assertNeedlesInHaystack(needles.ANONYMOUS_CONTROLS, resp.content)


class UnconfirmedUserTestCase(UIMixin, UnconfirmedProfileTestCase):
    def test_redirected_from_login(self):
        # Try to go there.
        resp = self.client.get(reverse('login'), follow=True)
        # Make sure they were sent to the dashboard page.
        self.assertDestPath(resp, 'confirm')

    def test_can_log_out(self):
        # Log them out.
        resp = self.client.get(reverse('logout'))
        self.assertRespStatusIs(resp, 302)

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
        self.assertDestPath(resp, 'confirm')
        self.assertNeedlesInHaystack(needles.UNCONFIRMED_CONTROLS, resp.content)

    def test_can_see_confirmation_form(self):
        resp = self.client.get(reverse('confirm'))
        self.assertNeedlesInHaystack(needles.CONFIRMATION_FORM, resp.content)
        self.assertNeedlesInHaystack(needles.UNCONFIRMED_CONTROLS, resp.content)

    def test_can_confirm(self):
        # Test the correct code, but with superfluous whitespace, and make
        # sure it goes through.
        correct_code = '{} '.format(self.profile.confirmation_code)
        resp = self.client.post(reverse('confirm'), {'code': correct_code}, follow=True)

        # We should end up at the dashboard.
        self.assertDestPath(resp, 'dashboard')
        self.assertNeedlesInHaystack(needles.DASHBOARD, resp.content)

        # Make sure the data was actually changed.
        updated_profile = Profile.objects.get(pk=self.profile.pk)
        self.assertEqual(updated_profile.confirmed_contact,
                         updated_profile.claimed_contact)

    def test_cannot_confirm_without_real_code(self):
        # Test a three-digit confirmation, which is shorter than it should
        # ever be (five digits with a four-digit fallback).
        resp = self.client.post(reverse('confirm'), {'code': '123'})
        self.assertRespStatusIs(resp, 200)

        # Make sure the data did not change.
        #updated_profile = Profile.objects.get(pk=self.profile.pk)
        self.assertEqual(None, self.profile.confirmed_contact)


class ConfirmedUserTestCase(UIMixin, ConfirmedProfileTestCase):
    PARTNER_KWARGS = [
        {'name': "Jimmy", "phone_number": '+19196499539'},
        {'name': "Frederik", "phone_number": '+19195555678', 'confirmed': True},
    ]

    def _create_partners(self):
        for p_kwargs in self.PARTNER_KWARGS:
            p_kwargs.update(profile=self.profile)
            Partnership.objects.create(**p_kwargs)
        
    def test_redirected_from_login(self):
        # Try to go there.
        resp = self.client.get(reverse('login'), follow=True)
        # Make sure they were sent to the dashboard page.
        self.assertDestPath(resp, 'dashboard')

    def test_can_log_out(self):
        # Log them out.
        resp = self.client.get(reverse('logout'))
        self.assertRespStatusIs(resp, 302)

        # Make sure they can't get to the dashboard now.
        resp = self.client.get(reverse('dashboard'), follow=True)
        # Make sure they were redirected.
        self.assertDestPath(resp, 'login')

    def test_can_see_personal_info(self):
        resp = self.client.get(reverse('dashboard'))
        self.assertRespStatusIs(resp, 200)
        self.assertNeedlesInHaystack(
                (self.profile.name,
                 self.profile.user.email,
                 str(self.profile.confirmed_contact.phone_number)),
                resp.content)

    def test_can_change_personal_info(self):
        pass

    def test_can_see_partners(self):
        # Create some partners!
        self._create_partners()

        # Make sure the dashboard shows them... or at least their names.
        resp = self.client.get(reverse('dashboard'))
        self.assertRespStatusIs(resp, 200)
        self.assertEqual(2, len(resp.context['partners']))
        self.assertNeedlesInHaystack(
                [p.name for p in self.profile.partnerships.all()],
                resp.content)

    def test_can_add_partners(self):
        # We shouldn't have any to start with.
        self.assertEqual(0, self.profile.partnerships.count())

        # Create each sample partner.
        for p_kwargs in self.PARTNER_KWARGS:
            resp = self.client.post(reverse('dashboard-partner'), p_kwargs)
            self.assertRespStatusIs(resp, 201)

        # Make sure they were created.
        self.assertEqual(2, self.profile.partnerships.count())
        # Make sure they aren't confirmed; the key for one of the requests
        # should have been ignored.
        for p in self.profile.partnerships.all():
            self.assertFalse(p.confirmed)

    def test_can_remove_partners(self):
        # Create some partners!
        self._create_partners()

        # Make sure the dashboard HTML has the 'remove' link for each partner.
        resp = self.client.get(reverse('dashboard'))
        self.assertNeedlesInHaystack(
                [reverse('dashboard-partner', kwargs={'pk': p.pk})
                 for p in self.profile.partnerships.all()],
                 resp.content)

        # Make sure that URL works.
        for p in self.profile.partnerships.all():
            resp = self.client.delete(reverse('dashboard-partner',
                                              kwargs={'pk': p.pk}))
            self.assertRespStatusIs(resp, 204)

        # Make sure we now have zero partners.
        resp = self.client.get(reverse('dashboard'))
        self.assertEqual(0, len(resp.context['partners']))
