from django.conf import settings
from django.db import models
from django.db.models import F, Sum

from django_twilio.client import twilio_client
from model_utils.models import TimeStampedModel
from phonenumber_field.modelfields import PhoneNumberField
import phonenumbers


class ContactManager(models.Manager):
    def get_num_messages_sent(self):
        """
        How many messages have we sent to all the users here? This will be
        especially useful for testing.
        """
        return (self.get_queryset().
                aggregate(num=Sum('num_messages_sent'))['num'])


class Contact(TimeStampedModel):
    phone_number = PhoneNumberField(db_index=True, unique=True)
    num_messages_sent = models.PositiveIntegerField(default=0)
    last_sid = models.CharField(max_length=34, blank=True, null=True)

    objects = ContactManager()

    def __unicode__(self):
        return unicode(self.phone_number)

    def delete(self, *args, **kwargs):
        """
        They shouldn't be able to delete.
        """
        raise NotImplementedError

    def log_sent_message(self, message):
        """
        Save automatically and atomically increment their message count.
        """
        if self.pk:
            self.num_messages_sent = F('num_messages_sent') + 1
        self.last_sid = message.sid
        self.save()

    def send_sms(self, body):
        """
        THE mechanism that sends a message to a user.

        This will send the message to the phone number and increment their
        message counter. If you're curious when they last received a message,
        the modified field is probably an accurate reflection.
        """

        # Send the SMS using the provided body.
        message = twilio_client.messages.create(
            body=body,
            to=str(self.phone_number),
            from_=settings.TWILIO_FROM_NUMBER,
        )

        # Increment the counter.
        self.log_sent_message(message)

    def get_last_sms(self):
        """
        Use last_sid to get the info on the last message they sent.
        """
        if not self.last_sid:
            return None
        try:
            return twilio_client.messages.list(sid=self.last_sid)[0]
        except IndexError:
            return None
