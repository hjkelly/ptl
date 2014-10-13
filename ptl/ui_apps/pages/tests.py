from django.conf import settings
from django.contrib.auth.models import User

from ...test import CleanTestCase

TEST_PH = settings.TEST_PHONE_NUMBER


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
                                     {'name': "Fred",
                                      'email': TEST_EMAIL,
                                      'password': 'yay!',
                                      'phone_number': TEST_PH},
                                     follow=True)
        self.assertEqual(200, post_resp.status_code,
                         msg="Didn't get the status code we expected. "
                             "Response:\n"+post_resp.content)
        # Make sure they were only redirected once, not to the login page as well.
        self.assertEqual(1, len(post_resp.redirect_chain),
                         msg="We were redirected more than once - possibly to "
                         "the login instead of directly to the dashboard?")
        self.assertTrue(post_resp.redirect_chain[0][0].endswith("/dashboard/"))

        # ... and that the DB reflects it.
        u = User.objects.get(username=TEST_EMAIL)
        self.assertGreater(u.profile.pk, 0)
        self.assertGreater(u.profile.contact.pk, 0)

    def test_alternative_syntax_registrations(self):
        """
        Make sure valid phone numbers and emails go through.
        """
        # Make sure the test number is ready to go.
        T = settings.TEST_PHONE_NUMBER[-10:]
        self.assertEqual(len(T), 10,
                         msg="Your test phone number must be of the format: "
                             "+1AAABBBCCCC (North American +1 followed by a "
                             "ten digits)")
        T1, T2, T3 = T[:3], T[3:6], T[6:]

        # Form alternative syntaxes and query.
        for i, ph in ((1, '{}-{}-{}'.format(T1, T2, T3)),
                      (2, '({}) {}-{}'.format(T1, T2, T3))):
            resp = self.client.post('/', {'name': "Fred",
                                          'email': "test{}@test.com".format(i),
                                          'password': "testpass",
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
                                   {'name': "Fred",
                                    'email': em,
                                    'password': pa,
                                    'phone_number': ph})
            self.assertEqual(200, resp.status_code)
        self.assertEqual(0, User.objects.count())
