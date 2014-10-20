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
        u = User.objects.create_user(username=email,
                                     email=email,
                                     password=password)

        # Now create the profile and return it.
        return super(ProfileManager, self).create(name=name, user=u,
                                                  claimed_contact=c)

    def confirmed_for_reminders(self):
        """
        Which users should receive text message reminders?
        """
        return self.get_queryset().filter(confirmed_contact__isnull=False)


class Profile(TimeStampedModel):
    # Django doesn't see that we're setting confirmation_code in the save(), so
    # have a default confirmation code just to make it happy. This will be four
    # digits instead of the usual five.
    DEFAULT_CONFIRMATION_CODE = '8143'
    user = models.OneToOneField(User, related_name='profile')
    name = models.CharField(max_length=25)
    claimed_contact = models.ForeignKey(Contact, related_name='profiles_claimed_by')
    confirmed_contact = models.OneToOneField(Contact,
                                             related_name='profile',
                                             blank=True,
                                             null=True)
    confirmation_code = models.CharField(max_length=5,
                                         default=DEFAULT_CONFIRMATION_CODE)

    objects = ProfileManager()

    def __unicode__(self):
        return u"Profile for {}".format(self.user.username)

    def generate_confirmation_code(self):
        """
        Only once, generate a reminder confirmation string.
        """
        # Be safe about it! Don't override an existing code.
        if (not self.confirmation_code or
            self.confirmation_code == self.DEFAULT_CONFIRMATION_CODE):

            # Generate a code between these numbers:
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
        body = ("This is a confirmation from Pass the Llama! Your code is "
                "{}. (Sorry if this is a wrong number!)".
                 format(self.confirmation_code))
        return self.claimed_contact.send_sms(body)

    def confirm(self):
        self.confirmed_contact = self.claimed_contact
        self.save()


@receiver(post_save, sender=Profile)
def send_confirmation_code_sms(sender, **kwargs):
    if kwargs['created'] == True:
        kwargs['instance'].send_confirmation_code()


class Partnership(models.Model):
    profile = models.ForeignKey(Profile, related_name='partnerships')
    contact = models.ForeignKey(Contact, related_name='partnerships')
    name = models.CharField(max_length=25)
    confirmation_string = models.CharField(max_length=10)
    confirmed = models.BooleanField(db_index=True, default=False)
