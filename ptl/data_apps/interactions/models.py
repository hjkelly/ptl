import re

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext as _

from model_utils import Choices


class Reminder(models.Model):
    profile = models.ForeignKey('profiles.Profile', related_name='reminders')
    timestamp = models.DateTimeField(auto_now_add=True)

    def clean(self):
        # Are they cleared to receive reminders? If not, complain.
        if not self.profile.confirmed_contact:
            raise ValidationError("Profile for user {} hasn't been confirmed, "
                                  "so we shouldn't send a reminder to them!".
                                  format(self.profile.user.username))

    def save(self, *args, **kwargs):
        """
        If the profile is confirmed, send the reminder and save.
        """
        self.full_clean()

        # Send the reminder message.
        body = ("Hey {}, have a llama! How have things been since your "
                "last check-in? Respond with good, bad, or ugly.".
                format(self.profile.name))
        self.profile.claimed_contact.send_sms(body)

        # Save as usual.
        return super(Reminder, self).save(*args, **kwargs)


class Checkin(models.Model):
    SPLIT_WORDS = re.compile('[^A-Za-z]+')
    STATUS_CODES = ('good', 'bad', 'ugly')
    STATUSES = Choices(
        (3, 'good', _("Good")),
        (2, 'bad', _("Bad")),
        (1, 'ugly', _("Ugly")),
    )

    profile = models.ForeignKey('profiles.Profile', related_name='checkins')
    contact = models.ForeignKey('sms.Contact', related_name='checkins')
    raw_body = models.TextField()
    status = models.PositiveSmallIntegerField(choices=STATUSES)
    timestamp = models.DateTimeField(auto_now_add=True)

    def get_status_code(self):
        """
        Return the first word of the body if it matches a status.
        """
        # Get the first word from the text.
        try:
            first_word = self.SPLIT_WORDS.split(self.raw_body)[0].lower()
        # If there are no discernible words, whoops...
        except IndexError:
            return None
        # If we have a word, try to figure out which status it could be.
        else:
            return first_word in self.STATUS_CODES and first_word or None

    def populate_status(self):
        """
        Use the status code to update the model's status field.
        """
        if not self.status:
            # What status does the text indicate?
            status_code = self.get_status_code()
            # Assign it to the model.
            if status_code:
                self.status = getattr(self.STATUSES, status_code)

    def populate_profile(self):
        if not self.profile_id:
            self.profile = self.contact.profile

    def is_valid(self):
        """
        Do we consider this a valid checkin?
        """
        # Populate the relevant data.
        self.populate_status()
        self.populate_profile()
        # If we could discern a status and there's at least one confirmed
        # profile associated with it?
        return bool(self.status and self.profile_id and self.profile.confirmed_contact)

    def save(self, *args, **kwargs):
        # Fill in the status field before saving.
        self.populate_status()
        # Also infer the profile.
        self.populate_profile()
        return super(Checkin, self).save(*args, **kwargs)


class PartnerReport(models.Model):
    profile = models.ForeignKey('profiles.Profile',
                                related_name='partner_reports')
    checkin = models.ForeignKey(Checkin, blank=True, null=True)
