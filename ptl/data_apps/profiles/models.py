from random import randint

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models, IntegrityError
from django.db.models.signals import post_save
from django.dispatch import receiver

from model_utils.models import TimeStampedModel
from phonenumber_field.phonenumber import PhoneNumber

from ..sms.models import Contact


class ProfileManager(models.Manager):
    def create(self, **kwargs):  #name, email, password, phone_number):
        """
        Create the User and Contact, then the Profile.
        """

        # Did they provide a phone number?
        phone_number = kwargs.pop('phone_number', None)
        if phone_number:
            # If so, make sure it exists and use it to get the claimed
            # contact for this account.
            kwargs['claimed_contact'], _ = Contact.objects.get_or_create(phone_number=phone_number)

        # Create the user, if they haven't provided one.
        if 'user' not in kwargs.keys():
            email = kwargs.pop('email')
            kwargs['user'] = User.objects.create_user(
                    username=email,
                    email=email,
                    password=kwargs.pop('password'))

        # Now create the profile and return it.
        return super(ProfileManager, self).create(**kwargs)

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
        Only once, generate a confirmation string.
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

    def send_confirmation_sms(self):
        """
        Send the confirmation text on their behalf.
        """
        # Don't send this if we've already confirmed them.
        if not self.confirmed_contact:
            # Have twilio send the confirmation message.
            body = ("This is a confirmation from Pass the Llama! Your code is "
                    "{}. (Sorry if this is a wrong number!)".
                     format(self.confirmation_code))
            return self.claimed_contact.send_sms(body)

    def confirm(self):
        self.confirmed_contact = self.claimed_contact
        self.save()

    def is_confirmed(self):
        return bool(self.confirmed_contact)

    def get_confirmed_partners(self):
        return list(self.partnerships.filter(confirmed=True).
                    values_list('contact', flat=True))


@receiver(post_save, sender=Profile)
def send_profile_confirmation_sms(sender, **kwargs):
    if kwargs['created'] == True:
        kwargs['instance'].send_confirmation_sms()


class PartnershipManager(models.Manager):
    def create(self, **kwargs):
        """
        Create the User and Contact, then the Profile.
        """

        # Get or create that contact.
        phone_number = kwargs.pop('phone_number', None)
        if phone_number:
            kwargs['contact'], _ = Contact.objects.get_or_create(
                    phone_number=phone_number)

        # Now create the profile and return it.
        return super(PartnershipManager, self).create(**kwargs)


class Partnership(models.Model):
    CONFIRMATION_STRING_LENGTH = 4

    profile = models.ForeignKey(Profile, related_name='partnerships')
    contact = models.ForeignKey(Contact, related_name='partnerships')
    name = models.CharField(max_length=25)
    # For the moment, this will be a slice of the profile's phone number.
    confirmation_string = models.CharField(max_length=10)
    confirmed = models.BooleanField(db_index=True, default=False)

    objects = PartnershipManager()

    class Meta:
        # If someone is asked to be a partner by more than one person, it's
        # possible the two profiles
        # A duplicate confirmation string for a given contact would make it
        # impossible for us to know whose notifications they're confirming,
        # so prevent that.
        unique_together = (
            ('profile', 'contact'),
            ('contact', 'confirmation_string'),
        )

    def _get_original_confirmation_string(self):
        return str(self.profile.confirmed_contact.phone_number)[
                -self.CONFIRMATION_STRING_LENGTH:]

    def generate_confirmation_code(self, duplicate_exists=False):
        """
        Generate a confirmation string.
        """
        # Don't generate a confirmation string if they already have one:
        if not self.confirmation_string:
            # Use the last four digits of the profile's phone number.
            self.confirmation_string = self._get_original_confirmation_string()
        # However, if they need a non-duplicate confirmation string, handle
        # that:
        elif duplicate_exists:
            # Generate a string of random numbers:
            self.confirmation_string = randint(1000, 9999)

    def save(self, *args, **kwargs):
        """
        Save as many times as needed to get a unique confirmation code.
        """

        # On first attempt, generate a confirmation code from the profile's
        # number.
        if not self.pk:
            self.generate_confirmation_code()

        # Save it until a confirmation code is unique... or realistically give
        # up after 10 times.
        tries = 0
        e = None
        while tries < 10:
            try:
                tries += 1
                super(Partnership, self).save(*args, **kwargs)
            except IntegrityError as e:
                self.generate_confirmation_code(duplicate_exists=True)
            else:
                return
        # If ten attempts didn't do the trick, give up.
        raise e

    def send_confirmation_sms(self):
        """
        Send a confirmation string to the user.
        """
        # Careful! Don't send this if we've already confirmed.
        if not self.confirmed:
            # Have twilio send the confirmation message.
            body = ("{} ({}) has added you as their partner on PassTheLlama.com. "
                    "Respond with {} to begin receiving their daily updates.".
                    format(self.profile.name,
                           self.profile.confirmed_contact.phone_number,
                           self.confirmation_string))
            return self.contact.send_sms(body)

    def get_absolute_url(self):
        return reverse('dashboard-partner', kwargs={'pk': self.pk})


@receiver(post_save, sender=Partnership)
def send_partnership_confirmation_sms(sender, **kwargs):
    if kwargs['created'] == True:
        kwargs['instance'].send_confirmation_sms()
