from django.db import models

from model_utils.models import TimeStampedModel
from phonenumber_field.modelfields import PhoneNumberField


class Contact(TimeStampedModel):
    phone_number = PhoneNumberField(unique=True)
    num_messages_sent = models.PositiveIntegerField(default=0)

    def delete(self, *args, **kwargs):
        """
        They shouldn't be able to delete.
        """
        raise NotImplementedError
