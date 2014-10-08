from django.contrib.auth.models import User
from django.db import models

from model_utils.models import TimeStampedModel
from phonenumber_field.phonenumber import PhoneNumber

from ..contacts.models import Contact


class ProfileManager(models.Manager):
    def create(self, email, password, phone_number):
        """
        Create the User and Contact, then the Profile.
        """

        # Create the phone number if it doesn't exist.
        c, _ = Contact.objects.get_or_create(phone_number=phone_number)

        # Create the user first.
        u = User.objects.create(username=email,
                                email=email,
                                password=password,
                                is_active=True)

        # Now create the profile and return it.
        return super(ProfileManager, self).create(user=u, contact=c)


class Profile(TimeStampedModel):
    user = models.OneToOneField('auth.User', related_name='profile')
    contact = models.OneToOneField('contacts.Contact', related_name='profile')
    subscription_confirmed = models.BooleanField(default=False)

    objects = ProfileManager()
