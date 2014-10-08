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
                                      'phone_number': '9876543210'})
        self.assertEqual(302, post_resp.status_code,
                         msg="Didn't get the status code we expected. "
                             "Response:\n"+post_resp.content)
        # ... and that the DB reflects it.
        u = User.objects.get(username=TEST_EMAIL)
        self.assertTrue(isinstance(u.profile, models.Model))
        self.assertTrue(isinstance(u.profile.contact, models.Model))

        u.delete()

    def test_alternative_syntax_registrations(self):
        """
        Make sure valid phone numbers and emails go through.
        """
        for em, pa, ph in (('b@gmail.com', 'password', '234-567-8901'),
                           ('c@gmail.com', 'passtest', '(345) 678-9012')):
            resp = self.client.post('/',
                                   {'email': em,
                                    'password': pa,
                                    'phone_number': ph})
            self.assertEqual(302, resp.status_code,
                             msg="Didn't get the status code we expected. "
                                 "Response:\n"+resp.content)
        self.assertEqual(3, User.objects.count())

    def test_bad_registrations(self):
        """
        Make sure bad data is rejected.
        """
        for em, pa, ph in (#('d@gmail.com', 'shortphone', '4567890'),
                           ('@invalid.com', 'password', '4567890123'),
                           ('not_an_email', 'password', '4567890123'),
                           ('spacez bad@gmail.com', 'password', '4567890123'),
                           ('', '<-- blank email == bad', '4567890123'),
                           ('empty_pass@gmail.com', '', '4567890123')):
            resp = self.client.post('/',
                                   {'email': em,
                                    'password': pa,
                                    'phone_number': ph})
            self.assertEqual(200, resp.status_code)
        self.assertEqual(0, User.objects.count())
