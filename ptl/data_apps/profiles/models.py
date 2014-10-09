from random import randint

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from model_utils.models import TimeStampedModel
from phonenumber_field.phonenumber import PhoneNumber

from ..sms.models import Contact


class ProfileManager(models.Manager):
    def create(self, name, email, password, phone_number):
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
        return super(ProfileManager, self).create(name=name, user=u, contact=c)


class Profile(TimeStampedModel):
    # Django doesn't see that we're setting confirmation_code in the save(), so
    # have a default confirmation code just to make it happy. This will be four
    # digits instead of the usual five.
    DEFAULT_CONFIRMATION_CODE = '8143'
    user = models.OneToOneField(User, related_name='profile')
    name = models.CharField(max_length=25)
    contact = models.ForeignKey(Contact, related_name='profile')
    confirmation_code = models.CharField(max_length=5,
                                         default=DEFAULT_CONFIRMATION_CODE)
    confirmed = models.BooleanField(default=False)

    objects = ProfileManager()

    def __unicode__(self):
        return u"Profile for {}".format(user.username)

    def generate_confirmation_code(self):
        """
        Only once, generate a reminder confirmation string.
        """
        # Be safe about it!
        if (not self.confirmation_code or
            self.confirmation_code == self.DEFAULT_CONFIRMATION_CODE):
            self.confirmation_code = str(randint(10000, 99999))

    def save(self, *args, **kwargs):
        if not self.pk:
            self.generate_confirmation_code()
        return super(Profile, self).save(*args, **kwargs)

    def send_confirmation_code(self):
        """
        Send the confirmation text on their behalf.
        """
        # Have twilio send the confirmation message.
        content = ("This is a confirmation from Pass the Llama! Your code is "
                   "{}. (Sorry if this is a wrong number!)".
                    format(self.confirmation_code))
        self.contact.send_sms(content)

    def send_reminder(self):
        """
        Have twilio send a reminder.
        """
        content = ("Hey {}, have a llama! How have things been since your "
                   "last check-in? Respond with good, bad, or ugly.".
                   format(self.name))
        self.contact.send_sms(content)


@receiver(post_save, sender=Profile)
def send_confirmation_code_sms(sender, **kwargs):
    if kwargs['created'] == True:
        kwargs['instance'].send_confirmation_code()
