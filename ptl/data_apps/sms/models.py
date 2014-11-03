from datetime import datetime, timedelta
from email.utils import parsedate_tz, mktime_tz
import sys

from django.conf import settings
from django.db import models
from django.db.models import F, Sum

from django_twilio.client import twilio_client
from model_utils.models import TimeStampedModel
from phonenumber_field.modelfields import PhoneNumberField
import phonenumbers


class Contact(TimeStampedModel):
    phone_number = PhoneNumberField(db_index=True, unique=True)

    def __unicode__(self):
        return unicode(self.phone_number)

    def delete(self, *args, **kwargs):
        """
        They shouldn't be able to delete.
        """
        raise NotImplementedError

    def send_sms(self, body):
        """
        Send an SMS to this contact.
        """
        return OutgoingSMS.objects.create(contact=self, body=body)


class OutgoingSMS(models.Model):
    """
    Stores an SMS that our system has sent.
    """

    contact = models.ForeignKey(Contact, related_name='outgoing_smses')
    body = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    twilio_sid = models.CharField(max_length=34, blank=True, null=True)

    def __unicode__(self):
        return u'To {}: {}'.format(self.contact.phone_number, self.body)

    def _send_via_twilio(self):
        """
        Actually send the message, if the circumstances call for it.
        """
        to_phone_number = str(self.contact.phone_number)
        # If they're testing, short circuit this and make it text us instead.
        if 'test' in sys.argv:
            to_phone_number = settings.TWILIO_FROM_NUMBER

        # Send the SMS using the provided body.
        message = twilio_client.messages.create(
            body=self.body,
            to=to_phone_number,
            from_=settings.TWILIO_FROM_NUMBER,
        )
        self.twilio_sid = message.sid

    def save(self, *args, **kwargs):
        # Send the message first, if that's what they want.
        self._send_via_twilio()
        return super(OutgoingSMS, self).save(*args, **kwargs)


class IncomingSMSManager(models.Manager):
    def fetch_from_twilio(self):
        """
        Process recent messages sent to us.

        This is a bit messy. There's no guarantee all new messages will show up
        with more recent timestamps, because they could be sent an hour ago but
        not received by Twilio, or received by Twilio but not processed until
        now. Because of this, we'll be forgiving with our cutoff.
        """
        filters = {
            'to': settings.TWILIO_FROM_NUMBER,
        }

        # If possible, only get messages we probably don't have yet (by using
        # the sent date of our most recent incoming message).
        try:
            most_recent_incoming_timestamp = (
                    self.get_queryset().
                    order_by('-twilio_date_sent')[0].
                    twilio_date_sent)
        except IndexError:
            most_recent_incoming_timestamp = datetime.now()

        # Only get the most recent messages.
        filters.update({
            # Back up - we need enough room to get up to 88 miles per hour.
            'after': most_recent_incoming_timestamp - timedelta(hours=1),
        })

        # Pull all incoming messages since then.
        for m in twilio_client.messages.list(**filters):
            # Convert the date from RFC 2822 to ISO 8601.
            datetime_date_sent = mktime_tz(parsedate_tz(m.date_sent))
            isoformat_date_sent = datetime.fromtimestamp(datetime_date_sent).isoformat()
            other_data = {
                'contact': Contact.objects.get(phone_number=m.from_),
                'body': m.body,
                'twilio_date_sent': isoformat_date_sent,
            }
            # Make sure the messages exist in our DB.
            self.get_or_create(twilio_sid=m.sid, defaults=other_data)


class IncomingSMS(models.Model):
    """
    Stores a message Twilio received on our behalf.
    """

    contact = models.ForeignKey(Contact, related_name='incoming_smses')
    body = models.TextField()
    twilio_sid = models.CharField(max_length=34, unique=True, db_index=True,
                                  blank=True, null=True)
    twilio_date_sent = models.DateTimeField(db_index=True)

    objects = IncomingSMSManager()

    class Meta:
        ordering = ('-twilio_date_sent',)

    def __unicode__(self):
        return u'From {}: {}'.format(self.contact.phone_number, self.body)
