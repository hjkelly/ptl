from django.contrib.auth.models import User

from ...test import CleanTestCase


class HomepageTests(CleanTestCase):
    def test_register(self):
        """
        Make sure we can load the homepage and register there.
        """
        TEST_EMAIL = 'the.test.user@gmail.com'

        # Make sure the user doesn't already exist.
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(username=TEST_EMAIL)

        # Make sure the page has the necessaries.
        get_resp = self.client.get('/')
        self.assertEqual(200, get_resp.status_code)
        self.assertContains(get_resp, "email")
        self.assertContains(get_resp, "password")
        self.assertContains(get_resp, "phone")
        self.assertContains(get_resp, "<form")

        # Make sure we can register...
        post_resp = self.client.post('/',
                                     {'email': TEST_EMAIL,
                                      'password': 'yay!',
                                      'phone_number': '9195555555'})
        self.assertEqual(302, post_resp.status_code,
                         msg="Didn't get the status code we expected. "
                             "Response:\n"+post_resp.content)
        # ... and that the DB reflects it.
        u = User.objects.get(username=TEST_EMAIL)
        self.assertGreater(u.profile.pk, 0)
        self.assertGreater(u.profile.contact.pk, 0)

        u.delete()

    def test_alternative_syntax_registrations(self):
        """
        Make sure valid phone numbers and emails go through.
        """
        for em, pa, ph in (('b@gmail.com', 'password', '919-555-5555'),
                           ('c@gmail.com', 'passtest', '(919) 555-5556')):
            resp = self.client.post('/',
                                   {'email': em,
                                    'password': pa,
                                    'phone_number': ph})
            self.assertEqual(302, resp.status_code,
                             msg="Didn't get the status code we expected. "
                                 "Response:\n"+resp.content)
        self.assertEqual(2, User.objects.count())

    def test_bad_registrations(self):
        """
        Make sure bad data is rejected.
        """
        for em, pa, ph in (#('d@gmail.com', 'shortphone', '5555550'),
                           ('@invalid.com', 'password', '9195555551'),
                           ('not_an_email', 'password', '9195555552'),
                           ('spacez bad@gmail.com', 'password', '9195555553'),
                           ('', '<-- blank email == bad', '9195555554'),
                           ('empty_pass@gmail.com', '', '9195555555')):
            resp = self.client.post('/',
                                   {'email': em,
                                    'password': pa,
                                    'phone_number': ph})
            self.assertEqual(200, resp.status_code)
        self.assertEqual(0, User.objects.count())
